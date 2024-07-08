let client_id = Date.now();
// document.querySelector("#ws-id").textContent = client_id;
// let session_id = Date.now() + "wsession"
const room = "2";
// document.querySelector(".tagline").textContent = room;
const ws = new WebSocket(`ws://localhost:8000/ws/${client_id}/${room}`);
let currentVideoPath = '';
const video = document.getElementById('my-player');
let vidSource = document.getElementById('video-source');
let peerConnections = {};
const configuration = {
    iceServers: [
		{
		  urls: "stun:stun.relay.metered.ca:80",
		},
		{
		  urls: "turn:global.relay.metered.ca:80",
		  username: "35d95514353e8310308a79a9",
		  credential: "NqTyFDOEFhAZnYed",
		},
		{
		  urls: "turn:global.relay.metered.ca:80?transport=tcp",
		  username: "35d95514353e8310308a79a9",
		  credential: "NqTyFDOEFhAZnYed",
		},
		{
		  urls: "turn:global.relay.metered.ca:443",
		  username: "35d95514353e8310308a79a9",
		  credential: "NqTyFDOEFhAZnYed",
		},
		{
		  urls: "turns:global.relay.metered.ca:443?transport=tcp",
		  username: "35d95514353e8310308a79a9",
		  credential: "NqTyFDOEFhAZnYed",
		},
	],
};
// const peerConnection = new RTCPeerConnection(configuration);

function getPeerConnection(client_id) {
    if (!peerConnections[client_id]) {
        const peerConnection = new RTCPeerConnection(configuration);
        peerConnections[client_id] = peerConnection;

        peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                ws.send(JSON.stringify({
                    type: 'candidate',
                    candidate: event.candidate,
                    client_id: client_id
                }));
            }
        };
        peerConnection.ontrack = (event) => {
            video.srcObject = event.streams[0];
        };
    }
    return peerConnections[client_id];
}



async function createAndSendOffer() {
    const peerConnection = getPeerConnection(client_id);
    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'offer',
            offer: offer,
            client_id: client_id
        }));
    }
}

function syncPlayback(time) {
    const diff = Math.abs(video.currentTime - time);
    if (diff > 1) {
        video.currentTime = time;
    }
}

async function handleOffer(offer, remoteClientId) {
    const peerConnection = getPeerConnection(remoteClientId);
    console.log('Handling offer:', offer);
    await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
    console.log('Peer connection state after setting remote description:', peerConnection.signalingState);
    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);

    ws.send(JSON.stringify({
        type: 'answer',
        answer: answer,
        client_id: remoteClientId
    }));

    ws.send(JSON.stringify({
        type: 'video_path',
        path: currentVideoPath,
        client_id: remoteClientId,
    }));
    // updateVideoPlayer(vidSource.src);

    ws.send(JSON.stringify({
        type: 'sync',
        time: video.currentTime,
        client_id: remoteClientId
    }));
}

async function handleCandidate(candidate, remoteClientId) {
    const peerConnection = getPeerConnection(remoteClientId);
    await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}
ws.onmessage = async (event) => {
    const data = JSON.parse(event.data);
    switch (data.type) {
        case 'offer':
            await handleOffer(data.offer, data.client_id);
            break;
        case 'candidate':
            await handleCandidate(data.candidate, data.client_id);
            break;
        case 'sync':
            syncPlayback(data.time);
            break;
        default:
            console.log(`Received unknown message type: ${data.type}`);
            break;
    }
};

ws.onerror = (event) => {
    console.error('WebSocket error:', event);
};

ws.onclose = (event) => {
    console.log('WebSocket closed:', event);
};


// ws.onopen = async (event) => {
//     console.log('WebSocket connection opened:', event);
//     await createAndSendOffer();
// };


