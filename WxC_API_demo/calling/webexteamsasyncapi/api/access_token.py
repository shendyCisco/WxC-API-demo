from typing import Optional, AsyncGenerator, List

from ..rest import RestSession
from ..util import to_camel, CamelModel

class Generate():
    grant_type: str
    client_id: str
    client_secret: str
    code: str
    redirect_uri: str

class Receive():
    access_token: str
    expires_in: int
    refresh_token: str
    refresh_token_expires_in: int

class Access_tokenAPI:
    def __init__(self, session: RestSession):
        self._session = session
        self._endpoint = self._session.endpoint("access_token")

    async def generate(self, grant_type: str = None, 
                        client_id: str = None, client_secret: str = None, 
                        code: str = None, redirect: str = None) -> Generate:
        params = {k: v for k, v in locals().items() if k != 'self' and v is not None}
        url = self._endpoint
        r = await self._session.post(url=url, json=params)
        return Recieve.parse_obj(r)