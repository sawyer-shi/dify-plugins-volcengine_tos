import os
import uuid
from datetime import datetime
from typing import Any, Dict, Generator, List
from collections.abc import Mapping

import tos
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File

from .utils import get_content_type_by_extension
import time

class MultiUploadFilesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            # 从运行时获取凭据并校验
            credentials = self.runtime.credentials if self.runtime else {}
            self._validate_credentials(credentials)
            
            # 执行多文件上传操作（使用运行时凭据）
            result = self._upload_files(tool_parameters, credentials)
            
            yield self.create_json_message(result)
            
            # 在text中输出成功信息，包含文件类型、大小（M单位）和访问链接
            files = tool_parameters.get('files', [])
            file_count = len(files)
            total_size = 0
            
            # 计算总文件大小
            for file in files:
                if isinstance(file, File) and hasattr(file, 'blob'):
                    total_size += len(file.blob)
                elif hasattr(file, 'read'):
                    # 保存当前文件指针位置
                    if hasattr(file, 'tell'):
                        current_pos = file.tell()
                    else:
                        current_pos = None
                    
                    # 读取文件内容获取大小
                    content = file.read()
                    total_size += len(content)
                    
                    # 重置文件指针
                    if hasattr(file, 'seek') and current_pos is not None:
                        file.seek(current_pos)
                elif isinstance(file, (str, bytes, os.PathLike)) and os.path.exists(file):
                    total_size += os.path.getsize(file)
            
            # 转换文件大小为MB
            total_size_mb = total_size / (1024 * 1024) if total_size > 0 else 0
            
            # 使用单独的字符串格式化 - 英文消息
            success_message = f"Successfully uploaded {file_count} files!\n"
            success_message += f"Total size: {total_size_mb:.2f} MB\n"
            success_message += "File URLs:\n"
            for i, file_info in enumerate(result.get('files', [])):
                success_message += f"{i+1}. {file_info['filename']}: {file_info['file_url']}\n"
            yield self.create_text_message(success_message)
        except Exception as e:
            # 在text中输出失败信息 - 英文消息
            yield self.create_text_message(f"Failed to upload files: {str(e)}")
            # 同时抛出异常以保持原有行为
            raise ValueError(f"Failed to upload files: {str(e)}")
    
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # 验证必填字段是否存在
        required_fields = ['endpoint', 'bucket', 'access_key_id', 'access_key_secret']
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                raise ValueError(f"Missing required credential: {field}")
    
    def _upload_files(self, parameters: dict[str, Any], credentials: dict[str, Any]) -> dict:
        try:
            # 获取文件数组、目录和其他参数
            files = parameters.get('files', [])
            directory = parameters.get('directory', '')
            directory_mode = parameters.get('directory_mode', 'no_subdirectory')
            filename_mode = parameters.get('filename_mode', 'filename')
            
            # 验证必填参数
            if not files:
                raise ValueError("Missing required parameter: files")
            
            # 验证文件数量限制（最多10个文件）
            if len(files) > 10:
                raise ValueError("Maximum number of files (10) exceeded")
            
            # 对directory进行前后去空格处理并允许为空（表示根目录）
            if directory is None:
                directory = ''
            directory = directory.strip()
            # 验证directory规则：禁止以空格、/或\\开头（仅当非空时）
            if directory and (directory.startswith(' ') or directory.startswith('/') or directory.startswith('\\')):
                raise ValueError("Directory cannot start with space, / or \\ ")
            
            # 验证认证参数（来自运行时凭据）
            required_auth_fields = ['endpoint', 'bucket', 'access_key_id', 'access_key_secret']
            for field in required_auth_fields:
                if field not in credentials or not credentials[field]:
                    raise ValueError(f"Missing required authentication parameter: {field}")
            
            # 初始化TOS客户端
            enable_verify_ssl = credentials.get('enable_verify_ssl', True)
            endpoint = credentials['endpoint']
            region = credentials.get('region')
            if not region:
                if '.' in endpoint:
                    region = endpoint.split('.')[0].replace('tos-', '')
                else:
                    region = ''
            request_timeout = int(parameters.get('request_timeout', 60))
            client = tos.TosClientV2(
                ak=credentials['access_key_id'],
                sk=credentials['access_key_secret'],
                endpoint=endpoint,
                region=region,
                enable_verify_ssl=enable_verify_ssl,
                request_timeout=request_timeout
            )
            
            # 处理目录路径
            current_date = datetime.now()
            date_path = ''
            if directory_mode == 'yyyy_mm_dd_hierarchy':
                date_path = f"{current_date.year}/{current_date.month:02d}/{current_date.day:02d}/"
            elif directory_mode == 'yyyy_mm_dd_combined':
                date_path = f"{current_date.year}{current_date.month:02d}{current_date.day:02d}/"
            
            # 生成带日期路径的完整目录
            full_directory = f"{directory}/{date_path}" if date_path else directory
            
            # 上传每个文件
            uploaded_files = []
            max_retries = int(parameters.get('max_retries', 3))
            
            for file in files:
                # 生成文件名
                source_file_name = "unknown"
                final_filename = None
                
                # 尝试从文件对象获取原始文件名和扩展名 - 加强版
                # 1. 处理dify_plugin的File对象
                if hasattr(file, 'name') and file.name:
                    original_filename = file.name
                    source_file_name = original_filename
                    file_base_name, file_extension = os.path.splitext(original_filename)
                    
                    # 生成最终文件名
                    if filename_mode == 'random':
                        # 使用UUID生成随机文件名
                        final_filename = f"{uuid.uuid4()}{file_extension}"
                    else:
                        # 使用原始文件名
                        final_filename = original_filename
                
                # 2. 尝试从file.filename获取（常见于某些Web框架）
                elif hasattr(file, 'filename') and file.filename:
                    original_filename = file.filename
                    source_file_name = original_filename
                    file_base_name, file_extension = os.path.splitext(original_filename)
                    
                    # 生成最终文件名
                    if filename_mode == 'random':
                        # 使用UUID生成随机文件名
                        final_filename = f"{uuid.uuid4()}{file_extension}"
                    else:
                        # 使用原始文件名
                        final_filename = original_filename
                
                # 3. 处理普通文件对象（如open()打开的文件）
                elif hasattr(file, 'name') and file.name and os.path.exists(file.name):
                    original_filename = os.path.basename(file.name)
                    source_file_name = original_filename
                    file_base_name, file_extension = os.path.splitext(original_filename)
                    
                    # 生成最终文件名
                    if filename_mode == 'random':
                        # 使用UUID生成随机文件名
                        final_filename = f"{uuid.uuid4()}{file_extension}"
                    else:
                        # 使用原始文件名
                        final_filename = original_filename
                
                # 4. 处理字节流对象（尝试从其属性获取扩展名）
                elif isinstance(file, bytes):
                    # 对于字节流，我们无法获取原始文件名，使用默认值
                    final_filename = f"{uuid.uuid4()}.dat"
                
                # 5. 处理字符串路径
                elif isinstance(file, str) and os.path.exists(file):
                    original_filename = os.path.basename(file)
                    source_file_name = original_filename
                    file_base_name, file_extension = os.path.splitext(original_filename)
                    
                    # 生成最终文件名
                    if filename_mode == 'random':
                        # 使用UUID生成随机文件名
                        final_filename = f"{uuid.uuid4()}{file_extension}"
                    else:
                        # 使用原始文件名
                        final_filename = original_filename
                
                # 处理文件名模式
                if filename_mode == 'filename_timestamp':
                    timestamp = current_date.strftime('%Y%m%d%H%M%S%f')[:-3]  # 保留毫秒
                    file_base, file_ext = os.path.splitext(final_filename)
                    final_filename = f"{file_base}_{timestamp}{file_ext}"
                
                # 生成对象键
                object_key = f"{full_directory}/{final_filename}" if full_directory else final_filename
                
                # 确保object_key不以/开头
                object_key = object_key.lstrip('/')
                
                # 准备文件内容
                file_content = None
                if isinstance(file, File):
                    # 处理dify_plugin的File对象
                    file_content = file.blob
                elif hasattr(file, 'read'):
                    # 处理文件对象
                    file_content = file.read()
                    # 重置文件指针
                    if hasattr(file, 'seek'):
                        file.seek(0)
                elif isinstance(file, str):
                    # 处理文件路径
                    if os.path.exists(file):
                        with open(file, 'rb') as f:
                            file_content = f.read()
                    else:
                        raise ValueError(f"File path does not exist: {file}")
                elif isinstance(file, bytes):
                    # 处理字节数据
                    file_content = file
                else:
                    raise ValueError("Unsupported file type")
                
                # 获取内容类型
                _, extension = os.path.splitext(final_filename)
                content_type = get_content_type_by_extension(extension)
                
                # 上传文件（增加重试与指数退避）
                last_error = None
                for attempt in range(1, max_retries + 1):
                    try:
                        client.put_object(
                            bucket=credentials['bucket'],
                            key=object_key,
                            content=file_content,
                            content_type=content_type
                        )
                        break
                    except Exception as e:
                        last_error = e
                        if attempt < max_retries:
                            time.sleep(min(8.0, 2 ** (attempt - 1)))
                        else:
                            raise ValueError(f"Failed to upload file {final_filename}: {str(last_error)}")
                
                # 构造文件访问URL
                file_url = f"https://{credentials['bucket']}.{credentials['endpoint']}/{object_key}"
                
                # 添加到已上传文件列表
                uploaded_files.append({
                    'filename': final_filename,
                    'object_key': object_key,
                    'file_url': file_url,
                    'content_type': content_type
                })
            
            # 返回结果
            return {
                'files': uploaded_files,
                'file_urls': [file_info['file_url'] for file_info in uploaded_files]
            }
        except Exception as e:
            raise ValueError(f"Failed to upload files: {str(e)}")