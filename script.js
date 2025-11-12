document.getElementById("uploadBtn").addEventListener("click", async () => {
    const audioFile = document.getElementById("audioInput").files[0];
    if (!audioFile) {
        alert("Please select an audio file first!");
        return;
    }

    const formData = new FormData();
    formData.append("audio", audioFile);

    document.getElementById("textOutput").textContent = "⏳ Processing audio...";
    document.getElementById("summaryOutput").textContent = "";
    document.getElementById("keywordsOutput").textContent = "";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            document.getElementById("textOutput").textContent = "❌ " + data.error;
            return;
        }

        document.getElementById("textOutput").textContent = data.text;
        document.getElementById("summaryOutput").textContent = data.summary;
        document.getElementById("keywordsOutput").textContent = data.keywords.join(", ");
    } catch (err) {
        document.getElementById("textOutput").textContent = "❌ Server Error!";
        console.error(err);
    }
});
