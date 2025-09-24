from typing import Any

# 尽早应用猴子补丁以避免SSL问题
try:
    from gevent import monkey
    monkey.patch_all(sys=True)
except ImportError:
    pass

import tos
from tos.auth import CredentialProviderAuth, StaticCredentialsProvider
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class VolcengineTosProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # 1. 检查必要凭据是否存在
            required_fields = ['access_key_id', 'access_key_secret', 'endpoint', 'bucket']
            for field in required_fields:
                if not credentials.get(field):
                    raise ToolProviderCredentialValidationError(f"{field} 不能为空")

            # 2. 提取访问密钥
            access_key_id = credentials['access_key_id']
            secret_key = credentials['access_key_secret']

            # 3. 验证directory和filename格式
            if 'directory' in credentials and credentials['directory']:
                dir_value = credentials['directory']
                if dir_value.startswith((' ', '/', '\\')):
                    raise ToolProviderCredentialValidationError("directory不能以空格、/或\\开头")

            if 'filename' in credentials and credentials['filename']:
                file_value = credentials['filename']
                if file_value.startswith((' ', '/', '\\')):
                    raise ToolProviderCredentialValidationError("filename不能以空格、/或\\开头")

            # 4. 从endpoint中提取region
            endpoint = credentials['endpoint']
            if '.' in endpoint:
                region = endpoint.split('.')[0].replace('tos-', '')
            else:
                region = credentials.get('region', '')

            # 5. 创建认证提供者并验证Bucket访问权限
            static_credentials = StaticCredentialsProvider(
                access_key_id=access_key_id,
                access_key_secret=secret_key
            )
            auth = CredentialProviderAuth(static_credentials, region)

            client = tos.TosClient(
                auth=auth,
                endpoint=endpoint,
                connect_timeout=credentials.get('timeout', 30)
            )

            response = client.list_buckets()
            print("Response类型:", type(response))
            print("Response属性列表:", dir(response))
            print("client.list_buckets() 获取到的bucket列表:", getattr(response, 'bucket_list', []))
            buckets = [b.name for b in getattr(response, 'bucket_list', [])]
            print("获取到的bucket名称列表:", buckets)
            if credentials['bucket'] not in buckets:
                raise ToolProviderCredentialValidationError(f"没有访问当前输入bucket名称 '{credentials['bucket']}' 的权限")

        except tos.exceptions.TosClientError as e:
            error_code = e.code
            if error_code == 'InvalidAccessKeyId':
                raise ToolProviderCredentialValidationError("无效的Access Key ID")
            elif error_code == 'SignatureDoesNotMatch':
                raise ToolProviderCredentialValidationError("Signature验证失败，请检查Secret Access Key是否正确")
            elif error_code == 'AccessDenied':
                raise ToolProviderCredentialValidationError("拒绝访问，请检查凭据权限")
            else:
                raise ToolProviderCredentialValidationError(f"TOS验证失败: {str(e)}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"凭据验证发生未知错误: {str(e)}")
