
let client_id = Date.now();
// document.querySelector("#ws-id").textContent = client_id;
let session_id = Date.now() + "wsession"
document.querySelector(".tagline").textContent = session_id;

var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}/${session_id}`);

let video = document.getElementById('my-player');
function updateVideoPlayer(filePath) {
	const fileExtension = filePath.split('.').pop().toLowerCase();
	const mimeTypes = {
		mp4: 'video/mp4',
		mkv: 'video/x-matroska',
		avi: 'video/x-msvideo',
		mov: 'video/quicktime',
		wmv: 'video/x-ms-wmv'
	};

	let source = document.createElement('source');
	source.src = filePath;
	source.type = mimeTypes[fileExtension] || 'video/mp4';
	if (video !== null) {
	video.innerHTML = '';
	video.appendChild(source);
	video.load();
	}
}

ws.onmessage = async function(event) {
	const data = JSON.parse(event.data);
	switch (data.type) {
		case 'offer':
			await handleOffer(data.offer, data.client_id);
			break;
		case 'answer':
			await handleAnswer(data.answer);
			break;
		case 'candidate':
			await handleCandidate(data.candidate);
			break;
		case 'sync':
			syncPlayback(data.time);
			break;
		default:
			appendMessage(event.data);
			break;
	}
};

ws.onmessage = function(event) {
		var messages = document.getElementById('messages')
		var message = document.createElement('li')
		var content = document.createTextNode(event.data)
		message.appendChild(content)
		messages.appendChild(message)
		const [command, timestamp] = event.data.split(':');
		switch (command) {
			case "play":
				// video.src = fetchVideo();
				video.currentTime = parseFloat(timestamp);
				video.play();
				break;
			case "pause":
				video.currentTime = parseFloat(timestamp);
				video.pause();
				break;
			case "seek":
				videoPlayer.currentTime = parseFloat(timestamp);
				break;
		}
	};
	function sendMessage(event) {
		var input = document.getElementById("messageText")
		ws.send(input.value)
		input.value = ''
		event.preventDefault()
	}

	function sendPlay() {
		const timestamp = videoPlayer.currentTime;
		ws.send(`play:${timestamp}`);
	}
	
	function sendPause() {
		const timestamp = videoPlayer.currentTime;
		ws.send(`pause:${timestamp}`);
	}
	
	function sendSeek(timestamp) {
		ws.send(`seek:${timestamp}`);
	}

