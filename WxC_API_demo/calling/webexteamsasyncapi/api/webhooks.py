from typing import Optional, AsyncGenerator, List

from ..rest import RestSession
from ..util import to_camel, CamelModel

class Webhook(CamelModel):
    id: str
    name: str
    target_url: str
    resource: str
    event: str
    org_id: str
    created_by: str
    app_id: str
    owned_by: str
    status: str
    created: str

class WebhookAPI:
    def __init__(self, session: RestSession):
        self._session = session
        self._endpoint = self._session.endpoint('webhooks')

    async def list(self, max: int = None) -> AsyncGenerator[Webhook, None]:
        
        params = {to_camel(k): v for k, v in locals().items() if v is not None}
        params.pop('self')

        url = self._endpoint
        #return self._session.pagination(url=url, params=params, factory=Webhook.parse_obj)
        return await self._session.get(url)

    async def create(self, name: str = None, target_url: str = None,
                        resource: str = None , 
                        event: str = None, 
                        filter: Optional[str] = None, 
                        secret: Optional[str] = None) -> Webhook:
        params = {to_camel(k): v for k, v in locals().items() if k != 'self' and v is not None}
        url = self._endpoint
        r = await self._session.post(url=url, json=params)
        return Webhook.parse_obj(r)

    async def delete(self, webhook_id) -> None:
        print("In api webhook delete")
        url = f'{self._endpoint}/{webhook_id}'
        await self._session.delete(url, success={204})