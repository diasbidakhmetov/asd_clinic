document.addEventListener("DOMContentLoaded", function () {
    let gazeDataByImage = {};
    let recording = false;
    let currentImage = ""; 

    webgazer.setGazeListener(function(data, elapsedTime) {
        if (data !== null && recording) {
            if (data.x >= 0 && data.y >= 0) {
                if (!gazeDataByImage[currentImage]) {
                    gazeDataByImage[currentImage] = [];
                }
                gazeDataByImage[currentImage].push({ x: data.x, y: data.y, time: elapsedTime });
            }
        }
    })
    .saveDataAcrossSessions(true)
    .showVideo(true)
    .showPredictionPoints(true)
    .begin();

    const images = [
        "/static/images/test_images/test_image_1.jpeg",
        "/static/images/test_images/test_image_2.jpeg",
        "/static/images/test_images/test_image_3.jpeg",
        "/static/images/test_images/test_image_4.jpeg",
        "/static/images/test_images/test_image_5.jpeg"
        // "/static/images/test_images/test_image_6.jpeg",
        // "/static/images/test_images/test_image_7.jpeg",
        // "/static/images/test_images/test_image_8.jpeg",
        // "/static/images/test_images/test_image_9.jpeg",
        // "/static/images/test_images/test_image_10.jpeg"
    ];
    const audios = [
        "/static/sounds/sound_1.mp3",
        "/static/sounds/sound_2.mp3",
        "/static/sounds/sound_3.mp3",
        "/static/sounds/sound_4.mp3",
        "/static/sounds/sound_5.mp3"
        // "/static/sounds/sound_6.mp3",
        // "/static/sounds/sound_7.mp3",
        // "/static/sounds/sound_8.mp3",
        // "/static/sounds/sound_9.mp3",
        // "/static/sounds/sound_10.mp3"
    ];
    let index = 0;
    const imageElement = document.getElementById("imageDisplay");
    const audioElement = document.getElementById("audioPlayer");
    const startButton = document.getElementById("startTest");
    let container  = document.getElementById("test-guide-container")

    async function changeMedia() {
        if (index > 0) {
            stopRecording();
        }
    
        if (index < images.length) {
            currentImage = images[index];
            imageElement.src = currentImage;
            audioElement.src = audios[index];
            audioElement.play();
            index++;
    
            startRecording();
            setTimeout(changeMedia, 10000);
        } else {
            stopRecording();
            saveCoordsToServer().then(() => {
                saveToServer();
            });            
        }
    }
    

    function startRecording() {
        recording = true;
    }

    async function saveToServer() {
        console.log("Отправка данных на сервер:", gazeDataByImage);
        try {
            const response = await fetch("/autizm_tests/save_gaze_data/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ gazeDataByImage })
            });
            const data = await response.json();
            console.log("Файл сохранён на сервере:", data);
    
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            }
        } catch (error) {
            console.error("Ошибка сохранения на сервер:", error);
        }
    }
    

    async function saveCoordsToServer() {
        const screenData = {
            width: screen.availWidth,
            height: screen.availHeight
        };

        try {
            const response = await fetch("/autizm_tests/save_screen_size/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(screenData)
            });
            const data = await response.json();
            console.log("Размер экрана сохранён:", data);
        } catch (error) {
            console.error("Ошибка сохранения размера экрана:", error);
        }
    }

    function stopRecording() {
        recording = false;
    }

    startButton.addEventListener("click", function () {
        webgazer.showVideo(false);
        startButton.style.display = "none";
        container.remove();
        changeMedia();
    });
});
