import os
from typing import Any, Dict
from collections.abc import Generator

import tos
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GetFileByUrlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            # 验证工具参数中的认证信息
            self._validate_credentials(tool_parameters)
            
            # 执行下载文件功能
            result = self._download_file(tool_parameters)
            
            # 返回JSON结果
            yield self.create_json_message(result)
            
            # 生成友好的文本消息
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
        required_fields = ['endpoint', 'bucket']
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                raise ValueError(f"Missing required credential: {field}")
        # access_key_id和access_key_secret将从provider获取，不需要在工具参数中验证
    
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
            
            # 获取认证信息
            credentials = self.runtime.get_credentials() if self.runtime else {}
            access_key_id = credentials.get('access_key_id') or parameters.get('access_key_id')
            access_key_secret = credentials.get('access_key_secret') or parameters.get('access_key_secret')
            
            # 验证认证信息
            if not access_key_id or not access_key_secret:
                raise ValueError("Missing required credential: access_key_id or access_key_secret")
            
            # 创建TOS客户端
            client = tos.TosClient(
                ak=access_key_id,
                sk=access_key_secret,
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