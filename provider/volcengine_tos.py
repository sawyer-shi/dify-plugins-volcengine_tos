from typing import Any

import tos
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class VolcengineTosProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # 验证必填字段是否存在
            required_fields = ['endpoint', 'bucket', 'access_key_id', 'access_key_secret']
            for field in required_fields:
                if field not in credentials or not credentials[field]:
                    raise ToolProviderCredentialValidationError(f"Missing required credential: {field}")
            
            # 创建TOS客户端进行凭证验证
            client = tos.TosClient(
                ak=credentials['access_key_id'],
                sk=credentials['access_key_secret'],
                endpoint=credentials['endpoint']
            )
            
            # 尝试获取存储桶信息以验证凭证有效性
            client.head_bucket(bucket=credentials['bucket'])
        except tos.exceptions.TosClientError as e:
            raise ToolProviderCredentialValidationError(f"TOS validation failed: {str(e)}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
