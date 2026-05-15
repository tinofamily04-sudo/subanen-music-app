const uploadBtn = document.getElementById('uploadBtn');
const musicFile = document.getElementById('musicFile');

const audioPlayer = document.getElementById('audioPlayer');
const resultsDiv = document.getElementById('results');

const originalLyrics = document.getElementById('originalLyrics');
const subanenLyrics = document.getElementById('subanenLyrics');

// LOADING ELEMENT
const loadingOverlay = document.getElementById('loadingOverlay');

// TEMPORARY LOCALHOST URL
const API_URL = "https://subanen-music-app-tino-01.onrender.com";

uploadBtn.addEventListener('click', async () => {
    const file = musicFile.files[0];

    if (!file) {
        alert("Please select a file first");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        // ✅ SHOW LOADING
        loadingOverlay.style.display = "flex";

        const response = await fetch(`${API_URL}/upload`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
            loadingOverlay.style.display = "none"; // hide on error
            return;
        }

        originalLyrics.textContent = data.original_lyrics;
        subanenLyrics.textContent = data.subanen_lyrics;

        audioPlayer.src = `${API_URL}/download/${data.filename}`;

        audioPlayer.style.display = "block";
        audioPlayer.load();

        resultsDiv.style.display = "block";

    } catch (err) {
        console.error(err);
        alert("Upload failed.");
    } finally {
        // ✅ HIDE LOADING ALWAYS
        loadingOverlay.style.display = "none";
    }
});