from django.shortcuts import render, redirect, get_object_or_404
from calling.webexteamsasyncapi import WebexTeamsAsyncAPI
import asyncio

import dateutil.parser

# Create your views here.
def index(request):
    for i in range(0, len(foo)):
        newDate = dateutil.parser.parse(str(foo[i]["time"]))
        foo[i]["time"] = newDate

    token = request.session.get('token', None)

    context = {
      "history_list" : foo,
      "activeCall_list" : activeCalls,
      "tokenOwner" : token,
      }
    return render(request, 'index.html', context = context)

def log_in(request):

    async def get_name():
        async with WebexTeamsAsyncAPI(access_token=token) as api:
            me = await api.people.me()
            print(me)
            return f'{me.first_name} {me.last_name}'

    if request.method == "POST":
        token = request.POST.get("tokenText")
        tokenOwner = asyncio.run(do_it())
        request.session["token"] = token
        request.session["tokenOwner"] = tokenOwner
        print("Post Ran")
    print(token)
    context = {
        "token" : token,
        "tokenOwner" : tokenOwner,
    }
    return redirect('/calling/')

def log_out(request):

    del request.session["token"]
    del request.session["tokenOwner"]

    return redirect('/calling/')

foo = [
{
    "type": "received",
    "name": "John Doe",
    "number": "1000",
    "privacyEnabled": False,
    "time": "2021-02-16T12:12:54.810-05:00"
},
{
    "type": "received",
    "name": "Reuben Walsh",
    "number": "1002",
    "privacyEnabled": False,
    "time": "2021-02-16T12:03:49.556-05:00"
},
{
    "type": "received",
    "name": "Reuben Walsh",
    "number": "1002",
    "privacyEnabled": False,
    "time": "2021-02-16T12:03:49.556-05:00"
},
{
    "type": "received",
    "name": "Reuben Walsh",
    "number": "1002",
    "privacyEnabled": False,
    "time": "2021-02-16T12:03:49.556-05:00"
},
{
    "type": "received",
    "name": "Reuben Walsh",
    "number": "1002",
    "privacyEnabled": False,
    "time": "2021-02-16T12:03:49.556-05:00"
},
{
    "type": "placed",
    "name": "Reuben Walsh",
    "number": "1002",
    "privacyEnabled": False,
    "time": "2021-02-16T11:36:26.507-05:00"
},
{
    "type": "placed",
    "name": "Reuben Walsh",
    "number": "1002",
    "privacyEnabled": False,
    "time": "2021-02-16T11:30:27.699-05:00"
},
{
    "type": "placed",
    "name": "Reuben Walsh",
    "number": "1002",
    "privacyEnabled": False,
    "time": "2021-02-16T11:29:18.990-05:00"
},
{
    "type": "placed",
    "name": "John Doe",
    "number": "1000",
    "privacyEnabled": False,
    "time": "2021-02-16T11:28:44.181-05:00"
},
{
    "type": "placed",
    "name": "Reuben Walsh",
    "number": "1002",
    "privacyEnabled": False,
    "time": "2021-02-16T11:22:28.955-05:00"
},
{
    "type": "placed",
    "name": "John Doe",
    "number": "1000",
    "privacyEnabled": False,
    "time": "2021-02-16T10:44:24.530-05:00"
},
{
    "type": "placed",
    "name": "John Doe",
    "number": "1000",
    "privacyEnabled": False,
    "time": "2021-02-16T10:40:45.347-05:00"
},
{
    "type": "placed",
    "name": "John Doe",
    "number": "1000",
    "privacyEnabled": False,
    "time": "2021-02-16T10:34:35.422-05:00"
},
{
    "type": "placed",
    "name": "John Doe",
    "number": "1000",
    "privacyEnabled": False,
    "time": "2021-02-16T10:33:32.380-05:00"
},
{
    "type": "missed",
    "name": "John Doe",
    "number": "1000",
    "privacyEnabled": False,
    "time": "2021-02-16T10:15:59.632-05:00"
},
{
    "type": "missed",
    "name": "John Doe",
    "number": "1000",
    "privacyEnabled": False,
    "time": "2021-02-16T10:15:30.260-05:00"
},
{
    "type": "missed",
    "name": "John Doe",
    "number": "1000",
    "privacyEnabled": False,
    "time": "2021-02-16T10:00:23.387-05:00"
}]

activeCalls = [
    {
        "id": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL0NBTEwvY2FsbGhhbGYtMTE4Nzg1Mzg5OjA",
        "callSessionId": "MjVhMTJjMzctOWMzZC00NGRmLTgyNTktNmQyYjY2YWU2MjJl",
        "personality": "originator",
        "state": "held",
        "remoteParty": {
            "name": "Reuben Walsh",
            "number": "1002",
            "personId": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1BFT1BMRS9lZmMwNzhhNS0yMmM4LTRiOGMtOTNhNy03ODkyZTdiNDFiN2M",
            "privacyEnabled": False,
            "callType": "location"
        },
        "appearance": 1,
        "created": "2021-02-17T13:11:38.512Z",
        "answered": "2021-02-17T13:11:41.505Z",
        "recordingState": "stopped"
    },
    {
        "id": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL0NBTEwvY2FsbGhhbGYtMTE4Nzg1Mzg5OjA",
        "callSessionId": "MjVhMTJjMzctOWMzZC00NGRmLTgyNTktNmQyYjY2YWU2MjJl",
        "personality": "originator",
        "state": "held",
        "remoteParty": {
            "name": "Reuben Walsh",
            "number": "1002",
            "personId": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1BFT1BMRS9lZmMwNzhhNS0yMmM4LTRiOGMtOTNhNy03ODkyZTdiNDFiN2M",
            "privacyEnabled": False,
            "callType": "location"
        },
        "appearance": 1,
        "created": "2021-02-17T13:11:38.512Z",
        "answered": "2021-02-17T13:11:41.505Z",
        "recordingState": "stopped"
    },
    {
        "id": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL0NBTEwvY2FsbGhhbGYtMTE4Nzg1Mzg5OjA",
        "callSessionId": "MjVhMTJjMzctOWMzZC00NGRmLTgyNTktNmQyYjY2YWU2MjJl",
        "personality": "originator",
        "state": "held",
        "remoteParty": {
            "name": "Reuben Walsh",
            "number": "1002",
            "personId": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1BFT1BMRS9lZmMwNzhhNS0yMmM4LTRiOGMtOTNhNy03ODkyZTdiNDFiN2M",
            "privacyEnabled": False,
            "callType": "location"
        },
        "appearance": 1,
        "created": "2021-02-17T13:11:38.512Z",
        "answered": "2021-02-17T13:11:41.505Z",
        "recordingState": "stopped"
    },
    {
        "id": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL0NBTEwvY2FsbGhhbGYtMTE4Nzg1Mzg5OjA",
        "callSessionId": "MjVhMTJjMzctOWMzZC00NGRmLTgyNTktNmQyYjY2YWU2MjJl",
        "personality": "originator",
        "state": "connected",
        "remoteParty": {
            "name": "Reuben Walsh",
            "number": "1002",
            "personId": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1BFT1BMRS9lZmMwNzhhNS0yMmM4LTRiOGMtOTNhNy03ODkyZTdiNDFiN2M",
            "privacyEnabled": False,
            "callType": "location"
        },
        "appearance": 1,
        "created": "2021-02-17T13:11:38.512Z",
        "answered": "2021-02-17T13:11:41.505Z",
        "recordingState": "stopped"
    },
    {
        "id": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL0NBTEwvY2FsbGhhbGYtMTE4Nzg1Mzg5OjA",
        "callSessionId": "MjVhMTJjMzctOWMzZC00NGRmLTgyNTktNmQyYjY2YWU2MjJl",
        "personality": "originator",
        "state": "held",
        "remoteParty": {
            "name": "Reuben Walsh",
            "number": "1002",
            "personId": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1BFT1BMRS9lZmMwNzhhNS0yMmM4LTRiOGMtOTNhNy03ODkyZTdiNDFiN2M",
            "privacyEnabled": False,
            "callType": "location"
        },
        "appearance": 1,
        "created": "2021-02-17T13:11:38.512Z",
        "answered": "2021-02-17T13:11:41.505Z",
        "recordingState": "stopped"
    },
]