import os
from typing import Any, Dict
from collections.abc import Generator

import tos
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File
from datetime import datetime

class VolcengineTosTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            # 验证工具参数中的认证信息
            self._validate_credentials(tool_parameters)
            
            # 根据操作类型执行不同的功能
            action = tool_parameters.get('action', 'upload').lower()
            
            if action == 'upload':
                result = self._upload_file(tool_parameters)
            elif action == 'download':
                result = self._download_file(tool_parameters)
            else:
                raise ValueError(f"Unsupported action: {action}. Supported actions are 'upload' and 'download'")
            
            # 返回JSON结果
            yield self.create_json_message(result)
            
            # 生成友好的文本消息
            if action == 'upload':
                file_size = result.get('file_size', 0)
                file_size_mb = file_size / (1024 * 1024) if file_size > 0 else 0
                success_message = "File uploaded successfully!\n"
                success_message += f"Filename: {result['filename']}\n"
                success_message += f"File type: {result.get('file_type', 'unknown')}\n"
                success_message += f"File size: {file_size_mb:.2f} MB\n"
                success_message += f"Access URL: {result['file_url']}\n"
                success_message += f"Object key: {result['object_key']}"
            else:  # download
                file_size = result.get('file_size', 0)
                file_size_mb = file_size / (1024 * 1024) if file_size > 0 else 0
                success_message = "File downloaded successfully!\n"
                success_message += f"Filename: {result['filename']}\n"
                success_message += f"File type: {result.get('file_type', 'unknown')}\n"
                success_message += f"File size: {file_size_mb:.2f} MB\n"
                success_message += f"Object key: {result['object_key']}\n"
                success_message += f"Content type: {result.get('content_type')}"
            
            yield self.create_text_message(success_message)
        except Exception as e:
            # 在text中输出失败信息 - 英文消息
            yield self.create_text_message(f"Operation failed: {str(e)}")
            # 同时抛出异常以保持原有行为
            raise ValueError(f"Operation failed: {str(e)}")
    
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # 验证必填字段是否存在
        required_fields = ['endpoint', 'bucket', 'access_key_id', 'access_key_secret']
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                raise ValueError(f"Missing required credential: {field}")
    
    def _upload_file(self, parameters: dict[str, Any]) -> dict:
        try:
            # 获取文件对象、目录和其他参数
            file = parameters.get('file')
            directory = parameters.get('directory', '').strip()
            directory_mode = parameters.get('directory_mode', 'no_subdirectory')
            filename = parameters.get('filename')
            filename_mode = parameters.get('filename_mode', 'filename')
            
            # 验证必填参数
            if not file:
                raise ValueError("Missing required parameter: file")
            
            # 生成文件名
            source_file_name = "unknown"
            if not filename:
                # 如果用户没有指定文件名，使用上传文件的原始文件名
                base_name = "upload"
                extension = ".dat"  # 默认扩展名
                
                # 尝试从文件对象获取原始文件名和扩展名
                if hasattr(file, 'name') and file.name:
                    original_filename = file.name
                    source_file_name = original_filename
                    file_base_name, file_extension = os.path.splitext(original_filename)
                    if file_extension:
                        extension = file_extension
                        base_name = file_base_name
                elif hasattr(file, 'filename') and file.filename:
                    original_filename = file.filename
                    source_file_name = original_filename
                    file_base_name, file_extension = os.path.splitext(original_filename)
                    if file_extension:
                        extension = file_extension
                        base_name = file_base_name
                
                # 尝试从文件内容类型推断扩展名
                if hasattr(file, 'content_type') and file.content_type:
                    extension = self._get_extension_from_content_type(file.content_type)
                
                # 确保扩展名是小写的，并且包含点号
                if extension and not extension.startswith('.'):
                    extension = '.' + extension
                extension = extension.lower()
                
                # 根据filename_mode处理文件名
                if filename_mode == 'filename_timestamp':
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
                    filename = f"{base_name}_{timestamp}{extension}"
                else:
                    filename = f"{base_name}{extension}"
            
            # 根据目录模式生成完整的文件路径
            object_key = self._generate_object_key(directory, directory_mode, filename)
            
            # 创建TOS客户端
            client = tos.TosClient(
                ak=parameters['access_key_id'],
                sk=parameters['access_key_secret'],
                endpoint=parameters['endpoint']
            )
            
            # 上传文件
            file_size = 0
            try:
                # 处理dify_plugin的File对象
                if isinstance(file, File):
                    file_content = file.blob
                    file_size = len(file_content)
                    client.put_object(
                        bucket=parameters['bucket'],
                        key=object_key,
                        content=file_content
                    )
                # 尝试作为普通文件对象处理
                elif hasattr(file, 'read'):
                    if hasattr(file, 'seek'):
                        file.seek(0)
                    file_content = file.read()
                    file_size = len(file_content)
                    client.put_object(
                        bucket=parameters['bucket'],
                        key=object_key,
                        content=file_content
                    )
                # 尝试作为文件路径处理
                elif isinstance(file, (str, bytes, os.PathLike)) and os.path.exists(file):
                    file_size = os.path.getsize(file)
                    client.upload_file(
                        bucket=parameters['bucket'],
                        key=object_key,
                        file_path=file
                    )
                else:
                    raise ValueError(f"Unsupported file type: {type(file)}")
            except Exception as e:
                raise ValueError(f"Failed to upload file: {str(e)}")
            
            # 构建文件URL
            protocol = 'https' if parameters.get('use_https', True) else 'http'
            file_url = f"{protocol}://{parameters['bucket']}.{parameters['endpoint']}/{object_key}"
            
            # 获取文件类型
            file_type = 'unknown'
            if extension:
                file_type = extension[1:].lower()
            
            return {
                "status": "success",
                "file_url": file_url,
                "filename": filename,
                "object_key": object_key,
                "message": "File uploaded successfully",
                "SourceFileName": source_file_name,
                "file_size": file_size,
                "file_type": file_type
            }
        except Exception as e:
            raise ValueError(f"Failed to upload file: {str(e)}")
    
    def _download_file(self, parameters: dict[str, Any]) -> dict:
        try:
            # 获取URL或object_key参数
            url = parameters.get('url')
            object_key = parameters.get('object_key')
            
            # 验证至少提供了一个参数
            if not url and not object_key:
                raise ValueError("Missing required parameter: either 'url' or 'object_key' must be provided")
            
            bucket = parameters['bucket']
            endpoint = parameters['endpoint']
            
            # 如果提供了URL，解析它
            if url:
                parsed_bucket, parsed_endpoint, parsed_object_key = self._parse_tos_url(url)
                object_key = parsed_object_key
                # 使用URL中的bucket和endpoint覆盖传入的参数（如果有）
                if parsed_bucket:
                    bucket = parsed_bucket
                if parsed_endpoint:
                    endpoint = parsed_endpoint
            
            # 创建TOS客户端
            client = tos.TosClient(
                ak=parameters['access_key_id'],
                sk=parameters['access_key_secret'],
                endpoint=endpoint
            )
            
            # 获取文件元信息
            head_response = client.head_object(
                bucket=bucket,
                key=object_key
            )
            
            # 读取文件内容
            response = client.get_object(
                bucket=bucket,
                key=object_key
            )
            file_content = response.read()
            
            # 获取文件大小
            file_size = head_response['content-length']
            
            # 获取文件内容类型
            content_type = head_response.get('content-type', 'application/octet-stream')
            
            # 生成文件名
            filename = parameters.get('filename')
            if not filename:
                # 从object_key中提取文件名
                filename = os.path.basename(object_key)
                if not filename:
                    filename = "download"
            
            # 从内容类型或文件名推断文件类型
            file_type = 'unknown'
            _, extension = os.path.splitext(filename)
            if extension:
                file_type = extension[1:].lower()
            else:
                # 尝试从content_type推断文件类型
                content_type_map = {
                    'image/': 'image',
                    'audio/': 'audio',
                    'video/': 'video',
                    'application/pdf': 'pdf',
                    'text/': 'text',
                    'application/json': 'json',
                    'application/xml': 'xml'
                }
                for ct, ft in content_type_map.items():
                    if content_type.startswith(ct):
                        file_type = ft
                        break
            
            return {
                "status": "success",
                "file_content": file_content,
                "filename": filename,
                "file_size": file_size,
                "content_type": content_type,
                "file_type": file_type,
                "object_key": object_key,
                "bucket": bucket,
                "endpoint": endpoint
            }
        except Exception as e:
            raise ValueError(f"Failed to download file: {str(e)}")
    
    def _generate_object_key(self, directory: str, directory_mode: str, filename: str) -> str:
        """根据目录模式生成完整的对象键"""
        # 确保目录名不以斜杠开头或结尾
        directory = directory.strip('/')
        
        # 基础路径就是一级目录
        base_path = directory
        
        # 根据目录模式添加日期相关的子目录
        if directory_mode == 'yyyy_mm_dd_hierarchy':
            now = datetime.now()
            base_path = os.path.join(directory, str(now.year), f"{now.month:02d}", f"{now.day:02d}")
        elif directory_mode == 'yyyy_mm_dd_combined':
            now = datetime.now()
            base_path = os.path.join(directory, now.strftime('%Y%m%d'))
        
        # 组合完整的对象键
        object_key = os.path.join(base_path, filename)
        
        # 将操作系统路径分隔符替换为TOS使用的斜杠
        return object_key.replace('\\', '/')
    
    def _parse_tos_url(self, url: str) -> tuple[str, str, str]:
        """解析TOS URL格式，提取bucket, endpoint和object_key"""
        import re
        # 尝试匹配TOS URL的多种格式
        
        # 格式1: https://bucket.endpoint/path/to/object
        pattern1 = r'^https?://([^.]+)\.([^/]+)/(.*)$'
        match1 = re.match(pattern1, url)
        
        if match1:
            return match1.group(1), match1.group(2), match1.group(3)
        
        # 格式2: https://bucket.endpoint
        pattern2 = r'^https?://([^.]+)\.([^/]+)$'
        match2 = re.match(pattern2, url)
        
        if match2:
            return match2.group(1), match2.group(2), ''
        
        # 如果以上格式都不匹配，抛出异常
        raise ValueError(f"Invalid TOS URL format: {url}")
    
    def _get_extension_from_content_type(self, content_type: str) -> str:
        """从内容类型推断文件扩展名"""
        content_type_map = {
            # 图片格式
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/bmp': '.bmp',
            'image/webp': '.webp',
            'image/svg+xml': '.svg',
            'image/tiff': '.tiff',
            'image/x-icon': '.ico',
            'image/heic': '.heic',
            
            # 音频格式
            'audio/mpeg': '.mp3',
            'audio/wav': '.wav',
            'audio/ogg': '.ogg',
            'audio/flac': '.flac',
            'audio/aac': '.aac',
            'audio/m4a': '.m4a',
            'audio/mp4': '.mp4',
            
            # 视频格式
            'video/mp4': '.mp4',
            'video/mov': '.mov',
            'video/avi': '.avi',
            'video/x-msvideo': '.avi',
            'video/x-ms-wmv': '.wmv',
            'video/webm': '.webm',
            'video/mpeg': '.mpg',
            
            # 文档格式
            'application/pdf': '.pdf',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.ms-excel': '.xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'application/vnd.ms-powerpoint': '.ppt',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
            
            # 文本格式
            'text/plain': '.txt',
            'text/csv': '.csv',
            'application/json': '.json',
            'application/xml': '.xml',
            'text/html': '.html',
            'text/css': '.css',
            'application/javascript': '.js',
            'text/markdown': '.md',
            
            # 压缩格式
            'application/zip': '.zip',
            'application/gzip': '.gz',
            'application/x-rar-compressed': '.rar',
            'application/x-7z-compressed': '.7z'
        }
        
        # 直接匹配内容类型
        if content_type in content_type_map:
            return content_type_map[content_type]
        
        # 尝试匹配内容类型的前缀
        for ct, ext in content_type_map.items():
            if content_type.startswith(ct):
                return ext
        
        # 如果没有匹配，返回默认扩展名
        return '.dat'
