

var width = 416; // We will scale the photo width to this
var height = 0; // This will be computed based on the input stream

var streaming = false;

var camera = null;
var video = null;
var canvas = null;
var canvas_container = null;
var canvas_container_close_button = null;
var photo = null;
var startbutton = null;
var clearbutton = null;

function startup() {
    camera = document.getElementById("camera");
    video = document.getElementById('video');
    canvas = document.getElementById('canvas');
    canvas_container = document.getElementById("canvas-container");
    canvas_container_close_button = document.getElementById("canvas-container-close-button");
    photo = document.getElementById('photo');
    startbutton = document.getElementById('startbutton');
    clearbutton = document.getElementById('clearbutton');



    navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false
        })
        .then(function(stream) {
            video.srcObject = stream;
            video.play();
        })
        .catch(function(err) {
            console.log("An error occurred: " + err);
        });

    video.addEventListener('canplay', function(ev) {
        if (!streaming) {
            height = video.videoHeight / (video.videoWidth / width);

            if (isNaN(height)) {
                height = width / (4 / 3);
            }


            video.setAttribute('width', width);
            video.setAttribute('height', height);
            canvas.setAttribute('width', width);
            canvas.setAttribute('height', height);
            streaming = true;
        }
    }, false);

    startbutton.addEventListener('click', function(ev) {
        takepicture();
        photo.classList.remove('d-none');
        camera.classList.add('d-none');
        startbutton.classList.add('d-none');
        clearbutton.classList.remove('d-none');
        ev.preventDefault();
    }, false);

    //clearphoto();

    clearbutton.addEventListener('click', function(event){
        clearphoto();
        photo.classList.add('d-none');
        camera.classList.remove('d-none');
        document.getElementById("image-data").value = "";
        clearbutton.classList.add('d-none');
        startbutton.classList.remove('d-none');
        event.preventDefault();
    }, false);

    //photo.style.height = ""+height+"px";
}


function clearphoto() {
    var context = canvas.getContext('2d');
    context.fillStyle = "#AAA";
    context.fillRect(0, 0, canvas.width, canvas.height);

    var data = canvas.toDataURL('image/jpg');
    photo.setAttribute('src', data);
    
}

function takepicture() {
    var context = canvas.getContext('2d');
    if (width && height) {
        canvas.width = width;
        canvas.height = height;
        context.drawImage(video, 0, 0, width, height);

        var data = canvas.toDataURL('image/jpg');
        photo.setAttribute('src', data);

        document.getElementById('image-data').value = data.split(',')[1];
    } else {
        clearphoto();
    }
}



window.addEventListener('load', startup, false);