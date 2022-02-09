from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from calling.webexteamsasyncapi import WebexTeamsAsyncAPI
import asyncio
import json
import requests
import uuid
import base64
from dateutil.parser import parse

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async

from calling import urls

from calling.models import WebexUserSession

# Create your views here.
def index(request):
    if request.method == "POST":
        pass
    else:
        token = request.session.get('token', None)
        tokenOwner = request.session.get('tokenOwner', None)
        # request.session.delete("tokenOwner")
        # request.session.delete("token")

        if token != None:
            return redirect(f"/calling/interface")
        
    
    return render(request, 'index.html')

#Interface
def interface(request, session_id = None):
    #get call history
    async def get_call_history():
        async with WebexTeamsAsyncAPI(access_token=token) as api:
            try:
                history = await api.call_controls.history() 
                return history
            except:
                return None

    async def get_calls():
        async with WebexTeamsAsyncAPI(access_token=token) as api:
            try:
                calls = await api.call_controls.calls()
                return calls
            except:
                return None
        
    def takeTime(elem):
        return elem.time

    token = request.session.get('token', None)
    print(token)
    tokenOwner = request.session.get('tokenOwner', None)

    #Create default variables incase nothing is filled, prevents error when making context and can be handled on template
    class history_list(): ##DOESN'T WORK IF NO CALLS HAVE BEEN MADE FROM ACCOUNT YET
        items = None
    call_list = None

    if request.method == "POST":
        pass
    else:
        if token != None:
            
            history_list = asyncio.run(get_call_history())
            call_list = asyncio.run(get_calls())
            #print(history_list)
            
            if history_list == None or call_list == None: #Handles if token expires while logged in
                # request.session.delete("token")
                # request.session.delete("tokenOwner")
                del request.session["token"]
                del request.session["tokenOwner"]
                return render(request, 'error.html', context={'message': 'There was a problem retrieving your information, please make sure your account has the correct priviledges.'})
        else:
            return render(request, 'error.html', context={'message': 'There was a problem retrieving your information, please make sure your account has the correct priviledges.'})

        # print(history_list[0].time)
        # print(len(history_list))
        if len(history_list) > 0:
            for i in range(0,len(history_list)):
                parsedDate = parse(str(history_list[i].time))
                history_list[i].time = parsedDate.strftime("%B %d, %Y, %H:%M %p")
        
            history_list.sort(reverse=True, key=takeTime)
    

    context = {
      "history_list" : history_list,
      "activeCall_list" : call_list,
      "tokenOwner" : tokenOwner,
    }
    return render(request, 'interface.html', context=context)


#Logging in/out
# def log_in(request):

#     async def get_name():
#         async with WebexTeamsAsyncAPI(access_token=token) as api:
#             me = await api.people.me()
#             print(me)
#             return f'{me.first_name} {me.last_name}'

#     if request.method == "POST":
#         token = request.POST.get("tokenText")
#         people_me_name = asyncio.run(get_name())
#         uniqueuid = uuid.uuid4()
#         request.session["token"] = token
#         request.session["tokenOwner"] = people_me_name
#         request.session["uuid"] = uniqueuid
#         request.session.set_expiry(43200)
#         #name_split = people_me_name.split()
#         #url_name = f"{name_split[0]}{name_split[1]}"
#         print(url_name)
#         print("Post Ran")
#     print(token)
#     context = {
#         "token" : token,
#         "tokenOwner" : people_me_name,
#     }
#     return redirect(f"/calling/interface/{uniqueuid}")

def log_out(request):

    del request.session["token"]
    del request.session["tokenOwner"]

    return redirect('/calling/')

def authenticate(request):

    async def generate_token():
        #async with WebexTeamsAsyncAPI() as api:
            # r = await api.access_token.generate(grant_type="authorization_code", 
            #                                         client_id="Cd612384d48b1561c4ae0066841a03d6eeb0ed0cf2b2d91308ec76d493cac3667",
            #                                         client_secret="c69a11d7850b0f717c9c75b70c4eb7edfeff145ec193703d29238bc9eb249bd5",
            #                                         code=code,
            #                                         redirect="http%3A%2F%2F192.168.1.105:8000%2Fcalling%2Fredirect%2F")
        uri = "https://webexapis.com/v1/access_token?"+"grant_type=authorization_code&"+"client_id=Cd612384d48b1561c4ae0066841a03d6eeb0ed0cf2b2d91308ec76d493cac3667&"+"client_secret=c69a11d7850b0f717c9c75b70c4eb7edfeff145ec193703d29238bc9eb249bd5&"+f"code={code}&"+"redirect_uri=http%3A%2F%2F192.168.1.139:8000%2Fcalling%2Fredirect%2F"
        header = {'Content-type': 'application/x-www-form-urlencoded'}
        r = requests.post(url=uri, headers=header)
        json_data = json.loads(r.text)
        return json_data

    async def get_name():
        async with WebexTeamsAsyncAPI(access_token=token) as api:
            me = await api.people.me()
            print(me)
            return f'{me.first_name} {me.last_name}'

    if request.method == "GET":
        print("Method == GET")
        if request.GET.get('state') == "AccessGranted":
            print("Access Granted!")
            code = request.GET.get('code')
            access_token_r = asyncio.run(generate_token())
            try:
                token = access_token_r['access_token']
            except Exception as e:
                print("Exception: ",e)
                print(access_token_r)
                return redirect("/calling/")
            people_me_name = asyncio.run(get_name())
            #uniqueuid = uuid.uuid4()
            request.session["token"] = token
            request.session["tokenOwner"] = people_me_name
            #request.session["uuid"] = str(uniqueuid)
            request.session.set_expiry(43200)

            return redirect(f"/calling/interface/") #{uniqueuid}")
            
        print(request.GET.get('state'))
        print("STATE WAS NOT ACCESSGRANTED")
        return redirect("/calling/") #If state is not what was sent
    else:
        return redirect("/calling/") #If not GET
            
        

#Dialing functions
# def dial(request):

#     async def dial(number):
#         async with WebexTeamsAsyncAPI(access_token=token) as api:
#             await api.call_controls.dial(number)

#     if request.method == "POST":
#         token = request.session["token"]
#         number = request.POST.get("numberSubmit")
#         print(number)
#         asyncio.run(dial(number))


#     return redirect('/calling/')

#Webhook Response Test

from calling.consumers import ChatConsumer

#from itty import *
import hashlib
import hmac

@csrf_exempt
def webhook(request):

    """
    When messages come in from the webhook, they are processed here.
    X-Spark-Signature - The header containing the sha1 hash we need to validate
    request.body - the Raw JSON String we need to use to validate the X-Spark-Signature
    """

    async def get_call_history():
        async with WebexTeamsAsyncAPI(access_token=token) as api:
            try:
                history = await api.call_controls.history() 
                return history
            except:
                return ["Failed"]
                
    key = b"somesupersecretphrase"
    raw = request.body

    #Let's create the SHA1 signature 
    #based on the request body JSON (raw) and our passphrase (key)
    hashed = hmac.new(key, raw, hashlib.sha1)
    validatedSignature = hashed.hexdigest()

    #print(f"Request:\n{request.headers.get('X-Spark-Signature')}\n\nValidSignature:\n{validatedSignature}\n")

    if validatedSignature == request.headers.get('X-Spark-Signature'): #Valid Response
        print("==Validated Webhook Response Recieved==")
        r_data = json.loads(raw)
        print(r_data)
        r_data['command'] = "call_update"
        channel = WebexUserSession.objects.get(webhook_id=r_data['id'])
        channel_layer = get_channel_layer()
        print(f"Sending to:\nChannel_name: {channel.channel_name}\nWebhook ID: {r_data['id']}")
        async_to_sync(channel_layer.send)(channel.channel_name, {
            'type': 'call.update',
            'text': json.dumps(r_data) 
        })
            

    else:
        print("==INVALID Webhook Response Recieved==")
        return HttpResponse(status=403)
    return HttpResponse(request)