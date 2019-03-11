/*
  操作：タッチパッド非対応のPCブラウザはasdwのみ。
  Android/iOSはタッチパッドで操作。
*/
var is_keyboard = false;
var is_touchpad = false;
VirtualJoystick.touchScreenAvailable() ? is_touchpad = true : is_keyboard = true
    
var tipsEL = document.getElementById('tips');
if(is_touchpad) {
    tipsEL.innerHTML = "Left: Steering. Right: Throttle."
} else {
    tipsEL.innerHTML = "a s d w keys."
}


function map(x, in_min, in_max, out_min, out_max) {
    /* 
       固定範囲内の入力値xの値を指定範内の値に変換して返す。
       例：0-10の範囲内の9の値を0-100の範囲内の90に変換する。
       result = map(9, 0, 10, 0, 100)

       Math.floor() will round in the wrong direction.
       before:
           return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
       after:
           var num = ~~(a / b);
         or 
           var num = (a / b) >> 0;
    */

    return (((x - in_min) * (out_max - out_min) / (in_max - in_min)) >> 0) + out_min
}

var joystickL = new VirtualJoystick({
	container: document.getElementById('container'),
    mouseSupport: false,
    stationaryBase: true,
    baseX: 100,
    baseY: window.innerHeight-120,
    strokeStyle	: 'cyan',
    limitStickTravel: true,
    stickRadius: 50
});

joystickL.addEventListener('touchStartValidation', function(event){
    var touch = event.changedTouches[0];
	if (touch.pageX < window.innerWidth/2) {
        console.log('Left down')
        return true;
    }
	return false
});

// one on the right of the screen
var joystickR = new VirtualJoystick({
	container: document.getElementById('container'),
    mouseSupport: false,
    stationaryBase: true,
    baseX: window.innerWidth-116,
    baseY: window.innerHeight-120,
    limitStickTravel: true,
    strokeStyle	: 'orange',
    stickRadius: 50
});

joystickR.addEventListener('touchStartValidation', function(event){
    var touch = event.changedTouches[0];
    if (touch.pageX >= window.innerWidth/2) {
        console.log('Right down')
        return true;
    }
    return false
});

var angle = 0;
var speed = 0;
if(is_keyboard) {
    var keyboard = new THREEx.KeyboardState();

    // only on keydown
    keyboard.domElement.addEventListener('keydown', function(event){
        if(keyboard.eventMatches(event, 'a')) {
            angle += 15
            if(angle > 45) {
                angle = 45
            }
        } else if(keyboard.eventMatches(event, 'd')) {
            angle -= 15
            if(angle < -45) {
                angle = -45
            }
        }

        if(keyboard.eventMatches(event, 's')) {
            speed -= 5
            if(speed < -100) {
                speed = -100
            }
        } else if(keyboard.eventMatches(event, 'w')) {
            speed += 5
            if(speed > 100) {
                speed = 100
            }
        }
    })
}

setInterval(function(){
    var outputEl = document.getElementById('result');

    if(is_touchpad) {
        // 仮想Joystickの値を表示する。
        // 入力範囲を適切な制御範囲に変換する
        angle = map(joystickL.deltaX(), -50, 50, -45, 45)
        speed = map(joystickR.deltaY(), -50, 50, -100, 100)
        // 角度は左をプラスに、速度は前進をプラスにする
        angle = -1 * angle
        speed = -1 * speed
        outputEl.innerHTML = '<b>Left:</b> '
            + ' dx:' + joystickL.deltaX()
            + ' dy:' + joystickL.deltaY()
            + (joystickL.right() ? ' right' : '')
            + (joystickL.up()    ? ' up'    : '')
            + (joystickL.left()  ? ' left'  : '')
            + (joystickL.down()  ? ' down'  : '')
            + '<br>'
            + '<b>Right:</b> '
            + ' dx:' + joystickR.deltaX()
            + ' dy:' + joystickR.deltaY()
            + (joystickR.right() ? ' right' : '')
            + (joystickR.up()    ? ' up'    : '')
            + (joystickR.left()  ? ' left'  : '')
            + (joystickR.down()  ? ' down'  : '')
    } else {
        outputEl.innerHTML = '<b>angle:</b> '
            + angle
            + '<br>'
            + '<b>speed:</b> '
            + speed
    }
    
    // 車両制御をPOSTメソッドで送信する
    var url = '/drive';
    var params = new FormData();
    params.append('angle', angle)
    params.append('speed', speed)
    var request = new XMLHttpRequest();
    request.open("POST", url, true);
    request.send(params);
}, 1/10 * 1000);
