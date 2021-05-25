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
    console.log(data.command)
    if (data.command == "call_update") {
        console.log("Sending to UpdateCall")
        UpdateCall(data.data);
    } else if (data.command == "history_update") {
        console.log("Sending to UpdateHistory")
        console.log(data.data)
        UpdateHistory(data.data);
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

function Retrieve() {
    var address = document.getElementById('dial_address').value;
    if (address != "") {
        console.log("Retrieving: "+address)
        var payload = `retrieve_${address}`
        socket.send(payload)
    }
}

// function CallIn_Animation(id) {
//     console.log("In CallIn_Animation")
//     var newHistoryCall = document.getElementById(id)
//     newHistoryCall.classList.add("show");
// }
// function CallOut_Animation(id) {
//     console.log("In CallOut_Animation")
//     var newHistoryCall = document.getElementById(id)
//     newHistoryCall.classList.remove("show");
// }

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
        console.log("In CallOut_Animation")
        var newHistoryCall = document.getElementById(data.callId)
        newHistoryCall.classList.remove("show")  //Fade Out Animation
        setTimeout(() => {
            document.getElementById(data.callId).remove();
            CheckAnyCalls()
        }, 200)
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
    setTimeout(function() {
        console.log("In CallIn_Animation")
        var newHistoryCall = document.getElementById(data.callId)
        newHistoryCall.classList.add("show")
    }, 3) //Fade In Animation
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
                <p>You can park a call against an extension, this extension can be retreived by another user. If the call isn't retrieved the parker of the call (you) will be recalled.<br>By selecting group park the destination will be ignored and anyone in the group park can pick up the call.</p>

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
        `<div class="LightBox_Background" id="LightBox_Background" onClick="HideLightBox()">
        </div>
        <div class="LightBox_Wrapper">
            <div class="LightBox flex flex-col centered whiteBackgroundText" id="LightBox" data-value="${id}">
                ${form}
                <input type="button" value="Submit" class="button positive" onClick="LightBoxSubmit('${purpose}')">
            </div>
        </div>`
    )
    setTimeout(function() {
        console.log("Lightbox Animation");
        document.getElementById("midpage").classList.add("blurred");
        document.getElementById("header").classList.add("blurred");
        document.getElementById("LightBox").classList.add("show");
        document.getElementById("LightBox_Background").classList.add("show");
    }, 3) //Fade In Animation
}
function HideLightBox() {
    console.log("in HideLightBox")
    document.getElementById("midpage").classList.remove("blurred");
    document.getElementById("header").classList.remove("blurred");
    document.getElementById("LightBox").classList.remove("show");
    document.getElementById("LightBox_Background").classList.remove("show");
    setTimeout(() => {
        document.getElementById("LightBox_Container").innerHTML = '';
    }, 200)

    // var midpageClass = document.getElementById("midpage").classList.remove("blurred")
    // var headerClass = document.getElementById("header").classList.remove("blurred")
    // console.log(document.getElementById("midpage").classList)

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
            var call_2 = document.getElementById("dropdown").value;
            var payload = `transfer_${id}_${call_2}`;
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

function UpdateHistory(data) {
    switch (data['type']) {
        case "received":
            var type = "<recieved>Recieved</recieved>";
            break;
        case "placed":
            var type = "<placed>Placed</placed>";
            break;
        case "missed":
            var type = "<missed>Missed</missed>";
            break;
        default:
            var type = "<unknown>Unknown</unknown>"
    }
    var entry = (
        `<div class="history-entry flex flex-row push-apart newHistoryCall" id="newHistoryCall">
            <p>${type} ${data['name']}
                <br>
                ${data['number']}
                <br>
                ${data['time']}
            </p>
            <button onclick="DoCommand('dial', '${data['number']}')" type="submit" name="numberSubmit" value="${data['number']}" class="button positive">Dial</button>
        </div>`
    );
    document.getElementById("CallHistory_Container").innerHTML = entry + document.getElementById("CallHistory_Container").innerHTML;
    //AddHistoryCall("newCall");
    setTimeout(function() {
        var newHistoryCall = document.getElementById("newHistoryCall")
        //newCall.style.height = "60px";
        newHistoryCall.removeAttribute("id");
        newHistoryCall.classList.remove("newHistoryCall");
    }, 3);
}

// function UpdateHistory(dataList) {

//     var htmlElements = ['<div class="spacer"></div>'];
//     console.log("In Update History")
//     console.log(dataList)
//     for (var data in dataList) {

//         // for(var property in data) {
//         //     console.log(property + "=" + data[property]);
//         //     for(var property_in in property) {
//         //         console.log(property_in + "=" + property[property_in]);
//         //     }
//         // }
//         console.log(`Entry: ${data}`)
//         switch (dataList[data]['type']) {
//             case "received":
//                 var type = "<recieved>Recieved</recieved>";
//                 break;
//             case "placed":
//                 var type = "<placed>Placed</placed>";
//                 break;
//             case "missed":
//                 var type = "<missed>Missed</missed>";
//                 break;
//             default:
//                 var type = "<unknown>Unknown</unknown>"
//         }
//         var entry = (
//             `<div class="history-entry flex flex-row push-apart">
//                 <p>${type} ${dataList[data]['name']}
//                     <br>
//                     ${dataList[data]['number']}
//                     <br>
//                     ${dataList[data]['time']}
//                 </p>
//                 <button onclick="DoCommand('dial', '${dataList[data]['number']}')" type="submit" name="numberSubmit" value="${dataList[data]['number']}" class="button positive">Dial</button>
//             </div>`
//         );
//         htmlElements.push(entry);
//         //document.getElementById("CallHistory_Container").innerHTML
//     }
//     document.getElementById("CallHistory_Container").innerHTML = ''
//     console.log(`Length of htmlElements: ${htmlElements.length}`)
//     htmlElements_length = htmlElements.length; //If i use raw value in for loop, it will only loop half times as .pop reduces the total entries each time. 
//     for (let i = 0; i < htmlElements_length; i++) {
//         console.log(`Popping: ${i}`)
//         call = htmlElements.pop()
//         //console.log("Writing to page", call)
//         document.getElementById("CallHistory_Container").innerHTML += call
//     }
// }