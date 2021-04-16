var loc = window.location

var wsStart = 'ws://'
if (loc.protocol == 'https:'){
    wsStart = 'wss://'
}

var endpoint = wsStart + loc.host + loc.pathname
console.log(endpoint)

var socket = new WebSocket(endpoint)
console.log(socket)

socket.onmessage = function(e){
    console.log("message", e)
    try {
        var data = JSON.parse(e.data);
    }catch {
        var data = e.data;
    }
        
    console.log(data)
    if (data.command == "call_update") {
        console.log("Sending to UpdateCall")
        UpdateCall(data.data);
    }
}
socket.onopen = function(e){
    console.log("open", e)
    //socket.send("Test Return Data")
}
socket.onerror = function(e){
    console.log("error", e)
}
socket.onclose = function(e){
    console.log("close", e)
}

function DoCommand(command, data) {
    if (typeof data == "object") {
        var payload = `${command}`
        for (i in data) {
            payload += `_${i}`
        }
    } else if (typeof data == "string") {
        var payload = `${command}_${data}`
    } else {
        payload = "Error"
    }

    console.log("send", payload)
    socket.send(payload)
}

function CustomDial() {
    var address = document.getElementById('dial_address').value;
    if (address != "") {
        console.log("Dialing: "+address)
        var payload = `dial_${address}`
        socket.send(payload)
    }
}

function UpdateCall(data) {
    console.log("Inside UpdateCall")
    console.log(data)
    if (data.state == 'connected') {
        connected = 'connected'
        hold_resume = `<input type="button" value="Hold" class="button dark" onClick="DoCommand('hold', this.parentNode.parentNode.parentNode.parentNode.id)">`
    } else if (data.state == 'held') {
        connected = ''
        hold_resume = `<input type="button" value="Resume" class="button dark" onClick="DoCommand('resume', this.parentNode.parentNode.parentNode.parentNode.id)">`
    } else if (data.state == 'disconnected') {
        console.log("In disconnect")
        document.getElementById(data.callId).remove();
        CheckAnyCalls()
        return;
    } else {
        connected = ''
        hold_resume = '<input type="button" value="Hold" class="button dark">'
    }

    try {
        var target = document.getElementById(data.callId); //Edit existing call
        target.innerHTML = (
            `<div>
                <p>
                    ${data.remoteParty.name} [${data.state}]
                    <br>
                    ${data.remoteParty.number}
                </p>
            </div>
            <div class="flex space-around">
                <form class="flex flex-row flex-wrap centered">
                    <div class="flex flex-col">
                        ${hold_resume}
                        <input type="button" value="Transfer" class="button dark" onClick="ShowLightBox('transfer', this.parentNode.parentNode.parentNode.parentNode.id)">  
                    </div>
                    <div class="flex flex-col">
                        <input type="button" value="Park" class="button dark" onClick="ShowLightBox('park', this.parentNode.parentNode.parentNode.parentNode.id)">  
                        <input type="button" value="Divert" class="button dark" onclick="ShowLightBox('divert', this.parentNode.parentNode.parentNode.parentNode.id)"> 
                    </div>
                    <input type="button" value="Hangup" class="button negative dark" onClick="DoCommand('hangup', this.parentNode.parentNode.parentNode.id)">  
                </form>
            </div>`
        )
        target.classList = `call whiteBackgroundText ${connected}`
        console.log("Edit Made")
    } catch (error) {
        console.log("Catch Running")
        //Create New call
        document.getElementById('Call_container').innerHTML = (
            document.getElementById('Call_container').innerHTML +
            `<div class="call whiteBackgroundText ${connected}" id="${data.callId}">
                <div>
                    <p>
                        ${data['remoteParty']['name']} [${data['state']}]
                        <br>
                        ${data.remoteParty.number}
                    </p>
                </div>
                <div class="flex space-around">
                    <form class="flex flex-row flex-wrap centered">
                        <div class="flex flex-col">
                            ${hold_resume}
                            <input type="button" value="Transfer" class="button dark" onClick="ShowLightBox('transfer', this.parentNode.parentNode.parentNode.parentNode.id)">  
                        </div>
                        <div class="flex flex-col">
                            <input type="button" value="Park" class="button dark" onClick="ShowLightBox('park', this.parentNode.parentNode.parentNode.parentNode.id)">  
                            <input type="button" value="Divert" class="button dark" onclick="ShowLightBox('divert', this.parentNode.parentNode.parentNode.parentNode.id)">  
                        </div>
                        <input type="button" value="Hangup" class="button negative dark" onClick="DoCommand('hangup', this.parentNode.parentNode.parentNode.id)">  
                    </form>
                </div>
            </div>`
        )
    }
    CheckAnyCalls()
}

function CheckAnyCalls() {
    divs = document.getElementsByClassName('call')
    console.log(`Found Div's ${divs}`)
    if (document.getElementById('Call_container').contains(divs[0])) {
        document.getElementById('No_calls').className = "whiteBackgroundText hidden";
    } else {
        document.getElementById('No_calls').className = "whiteBackgroundText shown";
    }
    
}

function ShowLightBox(purpose, id) {
    console.log("in ShowLightBox")
    switch (purpose) {
        case "park":
            var form = (
                `<h2>Park Call</h2>
                <p>###By diverting a call it will be redirected to the destination address, the destination will recieve a call from the current recipient.###</p>

                <div class="flex flex-row">
                    <div class="flex flex-col centered space-around">
                        <label>Destination: </label>
                        <label>Group Park: </label>
                    </div>
                    <div class="flex flex-col ">
                        <input id="destination" type="text" class="textbox formItemMargin" autocomplete="off" placeholder="Number or Extension">
                        <label class="switch formItemMargin">
                            <input type=checkbox id="isGroupPark">
                            <span class="slider round"></span>
                        </label>
                    </div>
                </div>
                `
            )
            break;
        case "transfer":
            var options = []
            var call_container = document.getElementById("Call_container");
            for (let i = 0; i < call_container.children.length; i++) {
                if (call_container.children[i].id != "No_calls" && call_container.children[i].id != id) {
                    options.push(`<option value=${call_container.children[i].id}>${call_container.children[i].children[0].children[0].innerHTML}</option>`)
                }
            }
            var form = (
                `<h2>Transfer Call</h2>
                <p>Transfering a call allows you to create a 1:1 call between two of your active calls. You will no longer be part of the call</p>
                <div class="flex flex-row centered">
                    <label class="formItemMargin">Transfer to: </label>
                    <select id="dropdown" class="formItemMargin dropdown">
                        ${options}
                    </select>
                </div>
                `
            )
            break;
        case "divert":
            var form = (
                `<h2>Divert Call</h2>
                <p>By diverting a call it will be redirected to the destination address, the destination will recieve a call from the current recipient.</p>

                <div class="flex flex-row">
                    <div class="flex flex-col centered space-around">
                        <label>Destination: </label>
                        <label>To Voicemail: </label>
                    </div>
                    <div class="flex flex-col ">
                        <input id="destination" type="text" class="textbox formItemMargin" autocomplete="off" placeholder="Number or Extension">
                        <label class="switch formItemMargin">
                            <input type=checkbox id="toVoiceMail">
                            <span class="slider round"></span>
                        </label>
                    </div>
                </div>
                `
            )
    }
    document.getElementById("LightBox_Container").innerHTML = (
        `<div class="LightBox_Background" onClick="HideLightBox()">
        </div>
        <div class="LightBox_Wrapper">
            <div class="LightBox flex flex-col centered whiteBackgroundText" id="LightBox" data-value="${id}">
                ${form}
                <input type="button" value="Submit" class="button positive" onClick="LightBoxSubmit('${purpose}')">
            </div>
        </div>`
    )
    document.getElementById("midpage").classList += " blurred"
    document.getElementById("header").classList += " blurred"
}
function HideLightBox() {
    console.log("in HideLightBox")
    document.getElementById("LightBox_Container").innerHTML = (
        ``
        
    )
    var midpageClass = document.getElementById("midpage").classList.remove("blurred")
    var headerClass = document.getElementById("header").classList.remove("blurred")
    console.log(document.getElementById("midpage").classList)

}

function LightBoxSubmit(purpose) {
    var id = document.getElementById("LightBox").getAttribute("data-value");
    switch (purpose) {
        case "park":
            var destination = document.getElementById("destination").value;
            var isGroupPark = document.getElementById("isGroupPark").checked;
            var payload = `park_${id}_${destination}_${isGroupPark}`
            break;
        case "transfer":
            var call_2 = document.getElementById("dropdown").value
            var payload = `transfer_${id}_${call_2}`
            break;
        case "divert":
            var destination = document.getElementById("destination").value;
            var toVoiceMail = document.getElementById("toVoiceMail").checked;
            var payload = `divert_${id}_${destination}_${toVoiceMail}`
    }
    console.log("send", payload)
    socket.send(payload)
    HideLightBox()
}