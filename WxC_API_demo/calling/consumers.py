import asyncio
import json
from django.contrib.auth import get_user_model
#from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from calling.webexteamsasyncapi import WebexTeamsAsyncAPI

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from calling.models import WebexUserSession


#from .models import Thread, ChatMessage
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        print("==Started Connect==")
        print(f"New Channel: {self.channel_name}")
        print(f"Channel Layer: {self.channel_layer}")
        async def create_webhook():
            async with WebexTeamsAsyncAPI(access_token=token) as api:
                apiResponse = await api.webhooks.create(name="Webex_Call_Controls_API_Demo", target_url="http://80.229.12.42:8000/calling/webhook/", resource="telephony_calls", event="all", secret="somesupersecretphrase")
                #print(f'\n--------API RESPONSE--------\n{apiResponse}\n---------------------------')
                return apiResponse
        
        @sync_to_async
        def create_record(webhook_id):
            WebexUserSession.objects.create(channel_name=self.channel_name, webhook_id=webhook_id)


        asyncio.sleep(1)
        self.username = self.scope["session"]["tokenOwner"]
        await self.accept()
        await self.send(text_data="[Welcome %s!]" % self.username)
        token = self.scope["session"]["token"]
        webhook_response = await create_webhook()
        await create_record(webhook_response.id)

        #await getCalls(token, self.channel_name, self.channel_layer)
        print("===Start Finished===")

        #print(self.channel_name)
        

    async def disconnect(self, message):

        async def delete_webhook(WebhookID):
            async with WebexTeamsAsyncAPI(access_token=token) as api:
                #print("In Delete_webhook")
                #result = record
                print(f'Record:\n--------\n{WebhookID}\n-------')
                await api.webhooks.delete(webhook_id=WebhookID)
                #print(f'Delete Response:\n{apiResponse}\n-------------')
                

        @sync_to_async
        def get_self_record():
            record = WebexUserSession.objects.filter(channel_name=closing_channel_name).values('webhook_id')
            print(record)
            WebhookID = record[0]["webhook_id"]
            return WebhookID

        @sync_to_async
        def delete_record():
            print("In Delete Record")
            WebexUserSession.objects.filter(channel_name=closing_channel_name).delete()
            #print(f"looking for: {self.channel_name}")
            #print("Record Deleted")

        token = self.scope["session"]["token"]
        closing_channel_name = self.channel_name
        print(f"Ending Channel: {closing_channel_name}")
        WebhookID = await get_self_record()
        print(WebhookID)
        await asyncio.gather(delete_webhook(WebhookID))
        await delete_record()
        print(f"Should have deleted: {closing_channel_name}")
        print("==Finished Disconnect==")

    async def receive(self, text_data=None, bytes_data=None):
        token = self.scope["session"]["token"]
        #print(text_data)
        instructions = text_data.split("_")
        params = instructions[1:]
        #print(instructions)
        # if instructions[0] == "getCalls":
        #     getCalls()

        if instructions[0] == 'dial':
            #print(f"Dial: {instructions[1]}")
            asyncio.create_task(dial(params[0],token))
        elif instructions[0] == 'hold':
            asyncio.create_task(hold(params[0],token))    
        elif instructions[0] == 'resume':
            asyncio.create_task(resume(params[0],token))    
        elif instructions[0] == 'hangup':
            asyncio.create_task(hangup(params[0],token))
        elif instructions[0] == 'divert':
            asyncio.create_task(divert(params,token)) 
        elif instructions[0] == 'transfer':
            asyncio.create_task(transfer(params,token)) 
        elif instructions[0] == 'park':
            asyncio.create_task(park(params,token)) 

    async def call_update(self, event):
        print("call_update Triggered")
        print(event)
        await self.send(text_data=event['text'])

# websocketDict = {}
# async def sendMessage(target,message):
#     print(f"Send message called: {message}\nTarget: {target}\nObject: {websocketDict[target]}")
#     ws = websocketDict[target]
#     await ws.send(text_data=message)

# async def getCalls(token, channel_name, channel_layer):
#     async with WebexTeamsAsyncAPI(access_token=token) as api:
#         r = await api.call_controls.calls()
#         print(f"Get Calls:\n{r}")
#         for i in r:
#             i["command"] = "call_update"
#             await channel_layer.send(channel_name, {
#                 "type": "call.update",
#                 "text": json.dumps(i)
#             })


async def dial(number, token):
    async with WebexTeamsAsyncAPI(access_token=token) as api:
        await api.call_controls.dial(number)

async def hold(call_id, token):
    print("in hold")
    async with WebexTeamsAsyncAPI(access_token=token) as api:
        await api.call_controls.hold(call_id)

async def resume(call_id, token):
    print("in resume")
    async with WebexTeamsAsyncAPI(access_token=token) as api:
        await api.call_controls.resume(call_id)

async def hangup(call_id, token):
    print("in hangup")
    async with WebexTeamsAsyncAPI(access_token=token) as api:
        await api.call_controls.hangup(call_id)

async def divert(params, token):
    print("in divert")
    print(params)
    if params[2] == "true":
        toVoicemail = True
    else:
        toVoicemail = False
    print(f"ToVoiceMail? {toVoicemail}")
    async with WebexTeamsAsyncAPI(access_token=token) as api:
        if params[1] == "":
            print("Not sending destination")
            await api.call_controls.divert(call_id=params[0], destination=None, to_voice_mail=toVoicemail)
        else:
            await api.call_controls.divert(call_id=params[0], destination=params[1], to_voice_mail=toVoicemail)

async def transfer(params, token):
    print("in transfer")
    print(params)
    async with WebexTeamsAsyncAPI(access_token=token) as api:
        await api.call_controls.transfer(call_id1=params[0],call_id2=params[1])

async def park(params, token):
    print("in park")
    print(params)
    async with WebexTeamsAsyncAPI(access_token=token) as api:
        await api.call_controls.park(call_id=params[0],destination=params[1], is_group_park=params[2])
    