var throttle = 1000;
var yaw = 1500;
var pitch = 1500;
var roll = 1500;

var leftX = null;
var leftY = null;
var rightX = null;
var rightY = null;


var setupFlightController = function(){
    fetch(
        '/config',
        {
            method: 'POST',
            body: JSON.stringify({
                "flightController": {
                    "start": true
                }
            }),
            cache: 'no-cache',
            headers: new Headers({
                'content-type': 'application/json'
            })
        }
    );
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
        '/command',
        {method: 'POST',
         body: JSON.stringify({
             'throttle': throttle,
             'yaw': yaw
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
        lctx.clearRect(0, 0, lc.width, lc.height);
        lctx.beginPath();
        lctx.arc(leftX, leftY, 50, 0, 2 * Math.PI);
        lctx.stroke();
        throttle = Math.round(2000 - leftY * 1000 / coords.height);
        yaw = Math.round(1000 + leftX * 2000 / coords.width);
        fetch(
            '/command',
            {method: 'POST',
             body: JSON.stringify({
                 'throttle': throttle,
                 'yaw': yaw
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
        '/command',
        {method: 'POST',
         body: JSON.stringify({
             'pitch': pitch,
             'roll': roll
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
        rctx.clearRect(0, 0, rc.width, rc.height);
        rctx.beginPath();
        rctx.arc(rightX, rightY, 50, 0, 2 * Math.PI);
        rctx.stroke();
        pitch = Math.round(1000 + rightY * 2000 / coords.height);
        roll = Math.round(1000 + rightX * 2000 / coords.width);
        fetch(
            '/command',
            {method: 'POST',
             body: JSON.stringify({
                 'pitch': pitch,
                 'roll': roll
             }),
             cache: 'no-cache',
             headers: new Headers({
                 'content-type': 'application/json'
             })
            }
        );
    }
});
