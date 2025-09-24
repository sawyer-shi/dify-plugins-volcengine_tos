import os
from typing import Any, Dict
from collections.abc import Generator

import tos
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File
from datetime import datetime

class UploadFileTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            # 验证工具参数中的认证信息
            self._validate_credentials(tool_parameters)
            
            # 执行上传文件功能
            result = self._upload_file(tool_parameters)
            
            # 返回JSON结果
            yield self.create_json_message(result)
            
            # 生成友好的文本消息
            file_size = result.get('file_size', 0)
            file_size_mb = file_size / (1024 * 1024) if file_size > 0 else 0
            success_message = "File uploaded successfully!\n"
            success_message += f"Filename: {result['filename']}\n"
            success_message += f"File type: {result.get('file_type', 'unknown')}\n"
            success_message += f"File size: {file_size_mb:.2f} MB\n"
            success_message += f"Access URL: {result['file_url']}\n"
            success_message += f"Object key: {result['object_key']}"
            
            yield self.create_text_message(success_message)
        except Exception as e:
            # 在text中输出失败信息 - 英文消息
            yield self.create_text_message(f"Operation failed: {str(e)}")
            # 同时抛出异常以保持原有行为
            raise ValueError(f"Operation failed: {str(e)}")
    
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # endpoint和bucket将从provider获取，不需要在工具参数中验证
        # access_key_id和access_key_secret将从provider获取，不需要在工具参数中验证
        pass
    
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
            
            # 获取认证信息
            credentials = self.runtime.get_credentials() if self.runtime else {}
            access_key_id = credentials.get('access_key_id')
            access_key_secret = credentials.get('access_key_secret')
            bucket = credentials.get('bucket')
            endpoint = credentials.get('endpoint')
            
            # 验证认证信息
            if not access_key_id or not access_key_secret or not bucket or not endpoint:
                raise ValueError("Missing required credential: access_key_id, access_key_secret, bucket or endpoint")
            
            # 创建TOS客户端
            client = tos.TosClient(
                ak=access_key_id,
                sk=access_key_secret,
                endpoint=endpoint
            )
            
            # 上传文件
            file_size = 0
            try:
                # 处理dify_plugin的File对象
                if isinstance(file, File):
                    file_content = file.blob
                    file_size = len(file_content)
                    client.put_object(
                        bucket=bucket,
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
                        bucket=bucket,
                        key=object_key,
                        content=file_content
                    )
                # 尝试作为文件路径处理
                elif isinstance(file, (str, bytes, os.PathLike)) and os.path.exists(file):
                    file_size = os.path.getsize(file)
                    client.upload_file(
                        bucket=bucket,
                        key=object_key,
                        file_path=file
                    )
                else:
                    raise ValueError(f"Unsupported file type: {type(file)}")
            except Exception as e:
                raise ValueError(f"Failed to upload file: {str(e)}")
            
            # 构建文件URL
            file_url = f"https://{bucket}.{endpoint}/{object_key}"
            
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