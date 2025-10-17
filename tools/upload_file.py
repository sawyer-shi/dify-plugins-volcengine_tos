import os
import uuid
from datetime import datetime
from typing import Any, Dict, Generator
from collections.abc import Mapping

import tos
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File

from .utils import get_content_type_by_extension
import time

class UploadFileTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            # 从运行时获取凭据并校验
            credentials = self.runtime.credentials if self.runtime else {}
            self._validate_credentials(credentials)
            
            # 执行文件上传操作（使用运行时凭据）
            result = self._upload_file(tool_parameters, credentials)
            
            yield self.create_json_message(result)
            
            # 生成详细的文本消息
            success_count = result.get('success_count', 0)
            error_count = result.get('error_count', 0)
            
            # 格式化文本消息
            text_message = f"File upload completed\n"
            text_message += f"Success: {success_count} file\n"
            text_message += f"Failed: {error_count} file\n\n"
            
            if success_count > 0:
                text_message += "Successful files:\n"
                for file_info in result.get('files', []):
                    if file_info.get('status') == 'success':
                        filename = file_info.get('filename', 'unknown')
                        file_size_mb = file_info.get('file_size_mb', 0)
                        file_size_bytes = file_info.get('file_size_bytes', 0)
                        file_type = file_info.get('file_type', 'unknown')
                        file_url = file_info.get('file_url', '')
                        
                        text_message += f"- File name: {filename}\n"
                        text_message += f"  File size: {file_size_mb:.2f} MB ({file_size_bytes} bytes)\n"
                        text_message += f"  File type: {file_type}\n"
                        text_message += f"  File URL: {file_url}\n\n"
            
            yield self.create_text_message(text_message)
        except Exception as e:
            # 在text中输出失败信息 - 英文消息
            yield self.create_text_message(f"Failed to upload file: {str(e)}")
            # 同时抛出异常以保持原有行为
            raise ValueError(f"Failed to upload file: {str(e)}")
    
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # 验证必填字段是否存在
        required_fields = ['endpoint', 'bucket', 'access_key_id', 'access_key_secret']
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                raise ValueError(f"Missing required credential: {field}")
    
    def _upload_file(self, parameters: dict[str, Any], credentials: dict[str, Any]) -> dict:
        try:
            # 获取文件对象、目录和其他参数
            file = parameters.get('file')
            directory = parameters.get('directory', '')
            directory_mode = parameters.get('directory_mode', 'no_subdirectory')
            filename = parameters.get('filename')
            filename_mode = parameters.get('filename_mode', 'filename')
            
            # 验证必填参数
            if not file:
                raise ValueError("Missing required parameter: file")
            
            # 对directory进行前后去空格处理并允许为空（表示根目录）
            if directory is None:
                directory = ''
            directory = directory.strip()
            # 验证directory规则：禁止以空格、/或\\开头（仅当非空时）
            if directory and (directory.startswith(' ') or directory.startswith('/') or directory.startswith('\\')):
                raise ValueError("Directory cannot start with space, / or \\ ")
            
            # 如果用户指定了filename，对其进行前后去空格处理
            if filename:
                filename = filename.strip()
                # 验证filename规则：禁止以空格、/或\开头
                if filename.startswith(' ') or filename.startswith('/') or filename.startswith('\\'):
                    raise ValueError("Filename cannot start with space, / or \\ ")
            
            # 验证认证参数（来自运行时凭据）
            required_auth_fields = ['endpoint', 'bucket', 'access_key_id', 'access_key_secret']
            for field in required_auth_fields:
                if field not in credentials or not credentials[field]:
                    raise ValueError(f"Missing required authentication parameter: {field}")
            
            # 生成文件名
            source_file_name = "unknown"
            if not filename:
                # 如果用户没有指定文件名，使用上传文件的原始文件名
                base_name = "upload"
                extension = ".dat"  # 默认扩展名
                
                # 尝试从文件对象获取原始文件名和扩展名 - 加强版
                # 1. 处理dify_plugin的File对象
                if hasattr(file, 'name') and file.name:
                    original_filename = file.name
                    source_file_name = original_filename
                    file_base_name, file_extension = os.path.splitext(original_filename)
                    if file_extension:
                        extension = file_extension
                        base_name = file_base_name
                
                # 2. 尝试从file.filename获取（常见于某些Web框架）
                elif hasattr(file, 'filename') and file.filename:
                    original_filename = file.filename
                    source_file_name = original_filename
                    file_base_name, file_extension = os.path.splitext(original_filename)
                    if file_extension:
                        extension = file_extension
                        base_name = file_base_name
                
                # 3. 处理普通文件对象（如open()打开的文件）
                elif hasattr(file, 'name') and file.name and os.path.exists(file.name):
                    original_filename = os.path.basename(file.name)
                    source_file_name = original_filename
                    file_base_name, file_extension = os.path.splitext(original_filename)
                    if file_extension:
                        extension = file_extension
                        base_name = file_base_name
                
                # 4. 处理字节流对象（尝试从其属性获取扩展名）
                elif isinstance(file, bytes):
                    # 对于字节流，我们无法获取原始文件名，使用默认值
                    pass
                
                # 5. 处理字符串路径
                elif isinstance(file, str) and os.path.exists(file):
                    original_filename = os.path.basename(file)
                    source_file_name = original_filename
                    file_base_name, file_extension = os.path.splitext(original_filename)
                    if file_extension:
                        extension = file_extension
                        base_name = file_base_name
                
                # 生成最终文件名
                if filename_mode == 'random':
                    # 使用UUID生成随机文件名
                    final_filename = f"{uuid.uuid4()}{extension}"
                else:
                    # 使用原始文件名或默认名称
                    final_filename = f"{base_name}{extension}"
            else:
                # 用户指定了文件名
                final_filename = filename
            # 从原始文件获取扩展名
            original_extension = ''
            # 1. 处理dify_plugin的File对象
            if hasattr(file, 'name') and file.name:
                _, original_extension = os.path.splitext(file.name)
            # 2. 尝试从file.filename获取
            elif hasattr(file, 'filename') and file.filename:
                _, original_extension = os.path.splitext(file.filename)
            # 3. 处理普通文件对象
            elif hasattr(file, 'name') and file.name and os.path.exists(file.name):
                _, original_extension = os.path.splitext(os.path.basename(file.name))
            # 4. 处理字符串路径
            elif isinstance(file, str) and os.path.exists(file):
                _, original_extension = os.path.splitext(os.path.basename(file))
            
            # 确保文件名包含原始扩展名
            if '.' not in final_filename and original_extension:
                final_filename += original_extension
            # 如果原始文件没有扩展名，不添加默认扩展名
            
            # 处理目录路径
            current_date = datetime.now()
            date_path = ''
            if directory_mode == 'yyyy_mm_dd_hierarchy':
                date_path = f"{current_date.year}/{current_date.month:02d}/{current_date.day:02d}"
            elif directory_mode == 'yyyy_mm_dd_combined':
                date_path = f"{current_date.year}{current_date.month:02d}{current_date.day:02d}"
            
            # 生成带日期路径的完整目录
            if date_path:
                if directory:
                    full_directory = f"{directory}/{date_path}"
                else:
                    full_directory = date_path
            else:
                full_directory = directory
            
            # 处理文件名模式
            if filename_mode == 'filename_timestamp':
                timestamp = current_date.strftime('%Y%m%d%H%M%S%f')[:-3]  # 保留毫秒
                file_base, file_ext = os.path.splitext(final_filename)
                final_filename = f"{file_base}_{timestamp}{file_ext}"
            
            # 生成对象键
            object_key = f"{full_directory}/{final_filename}" if full_directory else final_filename
            
            # 确保object_key不以/开头
            object_key = object_key.lstrip('/')
            
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
            
            # 准备文件内容和计算文件大小
            file_content = None
            file_size_bytes = 0
            
            try:
                if isinstance(file, File):
                    # 处理dify_plugin的File对象
                    file_content = file.blob
                    file_size_bytes = len(file.blob)
                elif hasattr(file, 'read'):
                    # 处理文件对象
                    file_content = file.read()
                    file_size_bytes = len(file_content)
                    # 重置文件指针
                    if hasattr(file, 'seek'):
                        file.seek(0)
                elif isinstance(file, str):
                    # 处理文件路径
                    if os.path.exists(file):
                        file_size_bytes = os.path.getsize(file)
                        with open(file, 'rb') as f:
                            file_content = f.read()
                    else:
                        raise ValueError(f"File path does not exist: {file}")
                elif isinstance(file, bytes):
                    # 处理字节数据
                    file_content = file
                    file_size_bytes = len(file)
                else:
                    raise ValueError("Unsupported file type")
                
                # 获取内容类型
                _, extension = os.path.splitext(final_filename)
                content_type = get_content_type_by_extension(extension)
                
                # 上传文件（增加重试与指数退避）
                max_retries = int(parameters.get('max_retries', 3))
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
                            raise ValueError(f"Failed to upload file: {str(last_error)}")
                
                # 构造文件访问URL
                file_url = f"https://{credentials['bucket']}.{credentials['endpoint']}/{object_key}"
                
                # 计算文件大小（MB）
                file_size_mb = file_size_bytes / (1024 * 1024) if file_size_bytes > 0 else 0
                
                # 获取文件类型（不带点）
                file_type = extension.lstrip('.') if extension else 'unknown'
                
                # 构建文件信息
                file_info = {
                    'filename': final_filename,
                    'object_key': object_key,
                    'file_url': file_url,
                    'content_type': content_type,
                    'file_size_bytes': file_size_bytes,
                    'file_size_mb': round(file_size_mb, 2),
                    'file_type': file_type,
                    'status': 'success'
                }
                
                # 返回结果
                return {
                    'status': 'completed',
                    'success_count': 1,
                    'error_count': 0,
                    'files': [file_info]
                }
            except Exception as e:
                # 返回失败结果
                file_info = {
                    'filename': final_filename or 'unknown',
                    'error': str(e),
                    'status': 'failed'
                }
                
                return {
                    'status': 'completed',
                    'success_count': 0,
                    'error_count': 1,
                    'files': [file_info]
                }
        except Exception as e:
            raise ValueError(f"Failed to upload file: {str(e)}")