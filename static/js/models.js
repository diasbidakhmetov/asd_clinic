function autoSaveModel() {
    Promise.all([
        localforage.getItem("webgazerGlobalData"),
        localforage.getItem("webgazerGlobalSettings")
    ]).then(([data, settings]) => {
        if (data && settings) {
            const model = { data, settings };
            fetch('/save_model/', { // Добавили слеш в URL
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model: model })
            }).then(response => response.json())
              .then(data => console.log("Авто-сохранение:", data.message))
              .catch(error => console.error("Ошибка авто-сохранения:", error));
        }
    });
}

function startAutoSave(interval = 30) {
    setInterval(autoSaveModel, interval * 1000);
}

function loadWebGazerModel() {
    fetch('/load_model/')
        .then(response => {
            if (!response.ok) {
                throw new Error("Нет сохраненной модели");
            }
            return response.json();
        })
        .then(data => {
            if (data.model) {
                localforage.setItem("webgazerGlobalData", data.model.data);
                localforage.setItem("webgazerGlobalSettings", data.model.settings);
                console.log("Модель загружена!");
            }
        })
        .catch(error => console.error("Ошибка загрузки модели:", error));
}

window.onload = function () {
    loadWebGazerModel();
    startAutoSave(30);
};
