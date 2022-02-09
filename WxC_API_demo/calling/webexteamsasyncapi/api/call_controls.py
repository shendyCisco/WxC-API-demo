from typing import Optional, AsyncGenerator, List

from ..rest import RestSession
from ..util import to_camel, CamelModel


class RemoteParty(CamelModel):
    name: str
    number: str
    person_id: str
    place_id: Optional[str]
    privacy_enabled: bool
    call_type: str

class RedirectingParty(CamelModel):
    name: str
    number: str
    person_id: str
    place_id: str
    privacy_enabled: bool
    call_type: str

class Party(CamelModel):
    name: str
    number: str
    person_id: str
    place_id: str
    privacy_enabled: bool
    call_type: str

class Redirections(CamelModel):
    reason: str
    redirecting_party: RedirectingParty

class Recall(CamelModel):
    type: str
    party: Party

class Call(CamelModel):
    id: str
    call_session_id: str
    personality: str
    state: str
    remote_party: Optional[RemoteParty]
    appearance: int
    created: str #ISO-8601 date
    answered: Optional[str] #ISO-8601 date
    redirections: Optional[List[Redirections]]
    recall: Optional[Recall]
    recording_state: str

class Item(CamelModel):
    type: str
    name: Optional[str]
    number: str
    privacy_enabled: bool
    time: str #ISO-8601 date

class History(CamelModel):
    items: List[Item]


class Post_Call(CamelModel): #Post fields
    # id: str
    # callId: str
    action: Optional[str]
    destination: Optional[str]
    toVoicemail: Optional[bool]
    callId1: Optional[str]
    callId2: Optional[str]
    isGroupPark: Optional[bool]
    
class Call_ControlsAPI:
    def __init__(self, session: RestSession):
        self._session = session
        self._endpoint = self._session.endpoint('telephony/calls')

    async def calls(self) -> Call:
        url = self._endpoint
        r = await self._session.get(url=url)
        activeCalls = []
        print(f"R = {r}")
        if r != {}:
            print("In If")
            for d in r['items']:
                print(f"D = {d}")
                activeCalls.append(d)
        print(f"Active Calls = {activeCalls}")
        return activeCalls
    
    async def history(self, type: Optional[str] = None) -> History:
        params = {to_camel(k): v for k, v in locals().items() if v is not None}
        params.pop('self')
        url = f'{self._endpoint}/history'
        r = await self._session.get(url=url, params=params)
        items = None
        try:
            history_list =  History.parse_obj(r)
            items = history_list.items
            print("Has History")
        except:
            print("No History")
            items = []
        return items

    async def dial(self, destination: str) -> Post_Call:
        params = {to_camel(k): v for k, v in locals().items() if k != 'self' and v is not None}
        url = f'{self._endpoint}/dial'
        r = await self._session.post(url=url, json=params, success={201})
        return Post_Call.parse_obj(r)
    
    async def retrieve(self, destination: str):
        url = f'{self._endpoint}/retrieve'
        r = await self._session.post(url=url, json={'destination': destination}, success={201})
        return Post_Call.parse_obj(r)

    async def hold(self, call_id: str):
        url = f'{self._endpoint}/hold'
        r = await self._session.post(url=url, json={'callId': call_id}, success={204})
        return r

    async def resume(self, call_id: str):
        url = f'{self._endpoint}/resume'
        r = await self._session.post(url=url, json={'callId': call_id}, success={204})
        return r

    async def hangup(self, call_id:str):
        url = f'{self._endpoint}/hangup'
        r = await self._session.post(url=url, json={'callId': call_id}, success={204})
        return r

    async def divert(self, call_id: str, destination: str = None, to_voicemail: bool = False):
        url = f'{self._endpoint}/divert'
        params = {to_camel(k): v for k, v in locals().items() if k != 'self' and v is not None}
        print(params)
        r = await self._session.post(url=url, json=params, success={204})
        return r

    async def transfer(self, call_id1: str, call_id2: str):
        url = f'{self._endpoint}/transfer'
        params = {'callId1': call_id1, 'callId2': call_id2}
        r = await self._session.post(url=url, json=params)
        return r

    async def park(self,call_id: str, destination: str = None, is_group_park: bool = None):
        url = f'{self._endpoint}/park'
        params = {to_camel(k): v for k, v in locals().items() if k != 'self' and v is not None}
        r = await self._session.post(url=url, json=params)
        return r