import asyncio
import json
from dateutil.parser import parse
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
        async def create_webhook():

            @sync_to_async
            def DeleteRecord(webhook):
                record = WebexUserSession.objects.filter(webhook_id=webhook['id']).delete()

            async with WebexTeamsAsyncAPI(access_token=token) as api:
                try:
                    apiResponse = await api.webhooks.create(name="Webex_Call_Controls_API_Demo", target_url="http://80.229.12.42:8000/calling/webhook/", resource="telephony_calls", event="all", secret="somesupersecretphrase")
                    #print(f'\n--------API RESPONSE--------\n{apiResponse}\n---------------------------')
                    return apiResponse
                except Exception as e:
                    if e.message == "Conflict": #Webook for target url already exists
                        r = await api.webhooks.list() #Generates list of webhooks
                        for webhook in r['items']:
                            if webhook['targetUrl'] == "http://80.229.12.42:8000/calling/webhook/": #Filters for all webhooks directed to this server
                                DeleteRecord(webhook) #Deletes Database Record (may have been left if websocket didn't close properly)
                                await api.webhooks.delete(webhook_id=webhook['id']) #Deletes Webhook
                        apiResponse = await api.webhooks.create(name="Webex_Call_Controls_API_Demo", target_url="http://80.229.12.42:8000/calling/webhook/", resource="telephony_calls", event="all", secret="somesupersecretphrase") #Creates new Webhook (remake to be sure config is correct)
                        return apiResponse #Return response
                    else:
                        self.close()        
                                
                    print(f'Expection:\n----\n{e.message}\n----')
        
        @sync_to_async
        def create_record(webhook_id):
            WebexUserSession.objects.create(channel_name=self.channel_name, webhook_id=webhook_id,) # group_name=self.user_room_name)
            print(f"Webhook ID: {webhook_id}")
            #self.WebexLocation = webhook_id[33:-35]
            #print(self.WebexLocation)


        asyncio.sleep(1)
        self.username = self.scope["session"]["tokenOwner"]
        # self.user = self.scope["session"]["tokenOwner"].replace(" ","")
        # self.user_room_name = "user_"+str(self.user) ##Notification room name
        # await self.channel_layer.group_add(
        #     self.user_room_name,
        #     self.channel_name
        # )
        await self.accept()
        await self.send(text_data="[Welcome %s!]" % self.username)
        token = self.scope["session"]["token"]
        webhook_response = await create_webhook()
        #self.channel_name = webhook_response.id #makes Channel name == webhook id
        await create_record(webhook_response.id)
        print(f"New Channel: {self.channel_name}")
        print(f"Webhook ID: {webhook_response.id}")

        #await getCalls(token, self.channel_name, self.channel_layer)
        print("===Start Finished===")

        #print(self.channel_name)
        

    async def disconnect(self, message):

        async def delete_webhook(WebhookID):
            async with WebexTeamsAsyncAPI(access_token=token) as api:
                #print("In Delete_webhook")
                #result = record
                #print(f'Record:\n--------\n{WebhookID}\n-------')
                await api.webhooks.delete(webhook_id=WebhookID)
                #print(f'Delete Response:\n{apiResponse}\n-------------')
                

        @sync_to_async
        def get_self_record():
            record = WebexUserSession.objects.filter(channel_name=closing_channel_name).values('webhook_id')
            #print(record)
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
        print(f"Webhook ID: {WebhookID}")
        await asyncio.gather(delete_webhook(WebhookID))
        await delete_record()
        #print(f"Should have deleted: {closing_channel_name}")
        print("==Finished Disconnect==")

    async def receive(self, text_data=None, bytes_data=None):
        print(f"Recieved Data for channel: {self.channel_name}")
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

        async def get_call_history():
            async with WebexTeamsAsyncAPI(access_token=token) as api:
                try:
                    history = await api.call_controls.history() 
                    return history
                except:
                    return ["Failed"]

        #@sync_to_async
        def takeTime(elem):
            return elem.time

        async def convertHistory(history_list):
            newList = []
            for i in range(0,len(history_list)): #Converts time to datetime.datetime
                parsedDate = parse(str(history_list[i].time))
                history_list[i].time = parsedDate
                newList.append(history_list[i].dict())
            return newList

        print(f"call_update Triggered on: {self.channel_name}")
        token = self.scope["session"]["token"]
        payload = json.loads(event['text'])

        if payload["data"]["eventType"] == "disconnected":
            #asyncio.sleep(5)
            history_list = await asyncio.gather(get_call_history())
            history_list = history_list[0]
            # print("\n\n")
            # print(history_list[0][0])

            #newList = await convertHistory(history_list) #Converts time to datetime.datetime
            newList=[]
            for i in range(0,len(history_list)): #Converts time to datetime.datetime
                parsedDate = parse(str(history_list[i].time))
                history_list[i].time = parsedDate

            print(history_list[0].time)
            sorted_list = sorted(history_list, key=takeTime) #sorts based on datatime

            #print(sorted_list)
            #for i in range(0,len(sorted_list)): #changes datatime to string 
            #    sorted_list[i].time = sorted_list[i].time.strftime("%B %d, %Y, %H:%M %p")
            #    newList.append(sorted_list[i].dict())

            sorted_list[-1].time = sorted_list[-1].time.strftime("%B %d, %Y, %H:%M %p")
            #newList.append(sorted_list[-1].dict())
            newElement = sorted_list[-1].dict()
                
            # print("\n\n")
            # print(type(history_list))
            # print("\n\n")
            # print(type(history_list[0]))
            # print(type(newlist))
            # print(newlist)
            dataDict = {"command": "history_update", "data": newElement}

            await self.send(text_data=json.dumps(dataDict))

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
            await api.call_controls.divert(call_id=params[0], destination=None, to_voicemail=toVoicemail)
        else:
            await api.call_controls.divert(call_id=params[0], destination=params[1], to_voicemail=toVoicemail)

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
    