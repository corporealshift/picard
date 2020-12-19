var socketClient = new WebSocket("ws://192.168.1.213:9001");
socketClient.onopen = function(evt) {
	
	socketClient.send("Test");

	document.getElementById("forward").addEventListener("touchstart", function(evt) {
		socketClient.send("throttle.forward");
	});

	document.getElementById("forward").addEventListener("touchend", function(evt) {
		socketClient.send("throttle.off");
	});

	document.getElementById("reverse").addEventListener("touchstart", function() {
		socketClient.send("throttle.reverse");
	});
	
	document.getElementById("reverse").addEventListener("touchend", function() {
		socketClient.send("throttle.off");
	});

	document.getElementById("left").addEventListener("touchstart", function() {
		socketClient.send("steering.left");
	});

	document.getElementById("left").addEventListener("touchend", function() {
		socketClient.send("steering.straight");
	});

	document.getElementById("right").addEventListener("touchstart", function() {
		socketClient.send("steering.right");
	});

	document.getElementById("right").addEventListener("touchend", function() {
		socketClient.send("steering.straight");
	});

};
socketClient.onmessage = function(event) {
	console.log("msg", event);
	var data = event.data.split(":");
	var key = data[0];

	switch(key) {
		case "distance":
			document.getElementById("distance").innerText = data[1];
			break;
		case "speed":
			document.getElementById("speed").innerText = data[1];
	}
};
