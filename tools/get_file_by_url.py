try:
    from gevent import monkey as _gevent_monkey
    _gevent_monkey.patch_all(ssl=False)
except Exception:
    pass
import os
import base64
from typing import Any, Dict
from collections.abc import Generator

# 提前导入 dify_plugin（其内部会触发 gevent 的 monkey patch），避免在 urllib3/ssl 之后再 patch
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import tos
from tos.auth import CredentialProviderAuth, StaticCredentialsProvider

# 禁用SSL验证警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 取消 requests 默认对 urllib3 的 pyOpenSSL 注入，避免 SSLContext.minimum_version 递归
try:
    import requests  # 触发 requests 导入（其会注入 pyOpenSSL）
    import urllib3.contrib.pyopenssl as pyopenssl
    pyopenssl.extract_from_urllib3()
except Exception:
    pass

# 兼容性补丁：避免 urllib3 在设置 context.minimum_version 时触发 RecursionError
try:
    import ssl as _stdlib_ssl
    import urllib3.util.ssl_ as _urllib3_ssl

    _ORIG_CREATE_CTX = _urllib3_ssl.create_urllib3_context

    def _safe_create_urllib3_context(*args, **kwargs):
        try:
            return _ORIG_CREATE_CTX(*args, **kwargs)
        except RecursionError:
            ssl_version = kwargs.get("ssl_version")
            ciphers = kwargs.get("ciphers")
            cert_reqs = kwargs.get("cert_reqs")
            options = kwargs.get("options")
            cadata = kwargs.get("cadata")
            protocol = ssl_version if isinstance(ssl_version, int) else (
                _stdlib_ssl.PROTOCOL_TLS_CLIENT if hasattr(_stdlib_ssl, "PROTOCOL_TLS_CLIENT") else _stdlib_ssl.PROTOCOL_TLS
            )
            ctx = _stdlib_ssl.SSLContext(protocol)
            if cert_reqs is not None:
                try:
                    ctx.verify_mode = cert_reqs
                except Exception:
                    pass
            if options is not None:
                try:
                    ctx.options |= options
                except Exception:
                    pass
            if ciphers is not None:
                try:
                    ctx.set_ciphers(ciphers)
                except Exception:
                    pass
            if cadata is not None:
                try:
                    ctx.load_verify_locations(cadata=cadata)
                except Exception:
                    pass
            return ctx

    _urllib3_ssl.create_urllib3_context = _safe_create_urllib3_context
except Exception:
    pass

# 进一步确保调用方使用安全的 create_urllib3_context（覆盖 urllib3.connection 中的同名绑定）
try:
    import urllib3.connection as _urllib3_conn
    _urllib3_conn.create_urllib3_context = _safe_create_urllib3_context
except Exception:
    pass

# 调试：验证补丁是否生效
try:
    import inspect as _inspect
    _util_is_safe = _urllib3_ssl.create_urllib3_context is _safe_create_urllib3_context
    _conn_is_safe = getattr(_urllib3_conn, "create_urllib3_context", None) is _safe_create_urllib3_context
    print(f"[SSL-PATCH] util_is_safe={_util_is_safe}, conn_is_safe={_conn_is_safe}")
except Exception:
    pass

class GetFileByUrlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            # 验证工具参数中的认证信息
            self._validate_credentials(tool_parameters)
            
            # 执行下载文件功能
            result, file_content = self._download_file(tool_parameters)
            
            # 返回JSON结果
            yield self.create_json_message({
                "files": [{
                    "file_name": result['filename'],
                    "file_size": result['file_size_bytes'],
                    "mime_type": result['content_type']
                }]
            })
            
            # 返回BLOB消息
            yield self.create_blob_message(
                blob=file_content,
                meta={
                    "filename": result['filename'],
                    "mime_type": result['content_type']
                }
            )
            
            # 生成友好的文本消息
            success_message = "File downloaded successfully!\n"
            success_message += f"Filename: {result['filename']}\n"
            success_message += f"File type: {result.get('file_type', 'unknown')}\n"
            success_message += f"File size: {result['file_size']:.2f} MB\n"
            success_message += f"Object key: {result['object_key']}\n"
            success_message += f"Content type: {result.get('content_type')}"
            
            yield self.create_text_message(success_message)
        except Exception as e:
            # 在text中输出失败信息 - 英文消息
            yield self.create_text_message(f"Operation failed: {str(e)}")
            # 避免递归错误，直接抛出原始异常
            raise e
    
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # endpoint和bucket将从provider获取，不需要在工具参数中验证
        # access_key_id和access_key_secret将从provider获取，不需要在工具参数中验证
        pass
    
    def _download_file(self, parameters: dict[str, Any]) -> tuple[dict, bytes]:
        try:
            # 获取URL参数
            url = parameters.get('url')
            
            # 验证URL参数
            if not url:
                raise ValueError("Missing required parameter: 'url' must be provided")
            
            # 获取认证信息
            credentials = self.runtime.credentials if self.runtime else {}
            access_key_id = credentials.get('access_key_id')
            access_key_secret = credentials.get('access_key_secret')
            bucket = credentials.get('bucket')
            endpoint = credentials.get('endpoint')
            region = credentials.get('region', '')
            enable_verify_ssl = credentials.get('enable_verify_ssl', False)
            
            # 从endpoint中提取region
            if '.' in endpoint:
                region = endpoint.split('.')[0].replace('tos-', '')
            else:
                region = credentials.get('region', '')         # 验证认证信息
            if not access_key_id or not access_key_secret or not bucket or not endpoint:
                raise ValueError("Missing required credential: access_key_id, access_key_secret, bucket or endpoint")
            
            # 解析URL
            parsed_bucket, parsed_endpoint, object_key = self._parse_tos_url(url)
            
            # 使用URL中的bucket和endpoint覆盖传入的参数（如果有）
            if parsed_bucket:
                bucket = parsed_bucket
            if parsed_endpoint:
                endpoint = parsed_endpoint
            
            # 创建TOS客户端
            client = tos.TosClientV2(
                ak=access_key_id,
                sk=access_key_secret,
                endpoint=endpoint,
                region=region,
                enable_verify_ssl=enable_verify_ssl,
                request_timeout=30
            )
            
            # 获取文件元信息
            file_content = None
            content_type = None
            file_size = 0
            
            # 尝试使用TOS客户端下载
            try:
                # 读取文件内容
                response = client.get_object(bucket=bucket, key=object_key)
                file_content = response.read()
                file_size = len(file_content)
                content_type = response.headers.get('Content-Type', 'application/octet-stream')
            except Exception as e:
                # 回退：尝试匿名HTTP下载（适用于对象公有读或临时授权URL）
                try:
                    import requests as _requests
                    _resp = _requests.get(url, stream=True, verify=enable_verify_ssl, timeout=30)
                    if _resp.status_code == 200:
                        file_content = _resp.content
                        file_size = int(_resp.headers.get('Content-Length', len(file_content)))
                        content_type = _resp.headers.get('Content-Type', 'application/octet-stream')
                    else:
                        raise e
                except Exception:
                    # 保持原始异常信息
                    raise e
            
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
            
            # 构建返回结果
            file_size_mb = file_size / (1024 * 1024) if file_size > 0 else 0
            result = {
                "filename": filename,
                "file_type": file_type,
                "file_size": round(file_size_mb, 2),
                "object_key": object_key,
                "content_type": content_type,
                "file_size_bytes": file_size
            }
            
            return result, file_content
        except Exception as e:
            raise e
        except Exception as e:
            # 避免递归错误，直接抛出原始异常
            raise e
    
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