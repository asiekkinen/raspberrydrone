var throttle = 1000;
var yaw = 1500;
var pitch = 1500;
var roll = 1500;

var leftX = null;
var leftY = null;
var rightX = null;
var rightY = null;


var connectionIntervalId = null;


var disconnect = function(e){
    clearInterval(connectionIntervalId);
    fetch(
        '/api',
        {
            method: 'POST',
            body: JSON.stringify({"alive": false}),
            cache: 'no-cache',
            headers: new Headers({
                'content-type': 'application/json'
            })
        }
    );
    e.innerText = "Disconnected";
}


var connect = function(e){
    e.innerText = "Disconnect";
    e.onclick = disconnect;
    connectionIntervalId = setInterval(function(){
        fetch(
                '/api',
                {
                    method: 'POST',
                    body: JSON.stringify({"alive": true}),
                    cache: 'no-cache',
                    headers: new Headers({
                        'content-type': 'application/json'
                    })
                }
            );
    }, 1000);
}


var lc = document.getElementById("leftCanvas");
var lctx = lc.getContext("2d");
lctx.beginPath();
lctx.arc(150, 300, 50, 0, 2 * Math.PI);
lctx.stroke();

var isLeftMouseDown = false;

var rc = document.getElementById("rightCanvas");
var rctx = rc.getContext("2d");
rctx.beginPath();
rctx.arc(150, 150, 50, 0, 2 * Math.PI);
rctx.stroke();

var isRightMouseDown = false;

lc.addEventListener("touchstart", e => {
    isLeftMouseDown = true;
});

lc.addEventListener("touchend", e => {
    isLeftMouseDown = false;
    var coords = lc.getBoundingClientRect();
    lctx.clearRect(0, 0, coords.width, coords.height);
    lctx.beginPath();
    lctx.arc(coords.width / 2, throttle < 1500 ? leftY : coords.height / 2, 50, 0, 2 * Math.PI);
    lctx.stroke();
    throttle = throttle < 1500 ? throttle : 1500;
    yaw = 1500;
    fetch(
        '/api',
        {
            method: 'POST',
            body: JSON.stringify({
                'command' : {
                    'throttle': throttle,
                    'yaw': yaw
                }
            }),
            cache: 'no-cache',
            headers: new Headers({
                'content-type': 'application/json'
            })
        }
    );
});

lc.addEventListener("touchmove", e => {
    if (isLeftMouseDown === true){
        var coords = lc.getBoundingClientRect();
        leftX = e.touches[0].clientX - coords.left;
        leftY = e.touches[0].clientY - coords.top;
        if (leftX < 0){
            leftX = 0;
        }
        if (leftX > lc.height) {
            leftX = lc.height;
        }

        if (leftY < 0){
            leftY = 0;
        }
        if (leftY > lc.width) {
            leftY = lc.width;
        }
        lctx.clearRect(0, 0, lc.width, lc.height);
        lctx.beginPath();
        lctx.arc(leftX, leftY, 50, 0, 2 * Math.PI);
        lctx.stroke();
        console.log(leftX);
        throttle = Math.round(2000 - leftY * 1000 / coords.height);
        yaw = Math.round(1000 + leftX * 1000 / coords.width);
        fetch(
            '/api',
            {
                method: 'POST',
                body: JSON.stringify({
                    'command' : {
                        'throttle': throttle,
                        'yaw': yaw
                    }
                }),
                cache: 'no-cache',
                headers: new Headers({
                    'content-type': 'application/json'
                })
            }
        );
    }
});


rc.addEventListener("touchstart", e => {
    isRightMouseDown = true;
});

rc.addEventListener("touchend", e => {
    isRightMouseDown = false;
    var coords = rc.getBoundingClientRect();
    rctx.clearRect(0, 0, coords.width, coords.height);
    rctx.beginPath();
    rctx.arc(coords.width / 2, coords.height / 2, 50, 0, 2 * Math.PI);
    rctx.stroke();
    pitch = 1500;
    roll = 1500;
    fetch(
        '/api',
        {
            method: 'POST',
            body: JSON.stringify({
                'command': {
                    'pitch': pitch,
                    'roll': roll
                }
            }),
            cache: 'no-cache',
            headers: new Headers({
                'content-type': 'application/json'
            })
        }
    );
});

rc.addEventListener("touchmove", e => {
    if (isRightMouseDown === true){
        var coords = rc.getBoundingClientRect();
        rightX = e.touches[0].clientX - coords.left;
        rightY = e.touches[0].clientY - coords.top;
        if (rightX < 0){
            rightX = 0;
        }
        if (rightX > rc.height) {
            rightX = rc.height;
        }

        if (rightY < 0){
            rightY = 0;
        }
        if (rightY > rc.width) {
            rightY = rc.width;
        }
        rctx.clearRect(0, 0, rc.width, rc.height);
        rctx.beginPath();
        rctx.arc(rightX, rightY, 50, 0, 2 * Math.PI);
        rctx.stroke();
        pitch = Math.round(2000 - rightY * 1000 / coords.height);
        roll = Math.round(1000 + rightX * 1000 / coords.width);
        fetch(
            '/api',
            {
                method: 'POST',
                body: JSON.stringify({
                    'command': {
                        'pitch': pitch,
                        'roll': roll
                    }
                }),
                cache: 'no-cache',
                headers: new Headers({
                    'content-type': 'application/json'
                })
            }
        );
    }
});
