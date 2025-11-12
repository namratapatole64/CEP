from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from pydub import AudioSegment
import whisper
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

# -------------------- Config --------------------
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set FFmpeg path explicitly for Windows
os.environ["FFMPEG_BINARY"] = r"C:\Users\Namrata\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_8wekyb3d8bbwe\LocalCache\Local\bin\ffmpeg.exe"

# Load Whisper model (small is good for CPU)
print("⏳ Loading Whisper model...")
model = whisper.load_model("small")
print("✅ Whisper model loaded!")

# -------------------- Home route --------------------
@app.route('/')
def index():
    return render_template('index.html')

# -------------------- Upload and process audio --------------------
@app.route('/upload', methods=['POST'])
def upload_audio():
    try:
        file = request.files.get('audio')
        if not file:
            return jsonify({"error": "No audio file uploaded"}), 400

        # Save file safely
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        filepath = os.path.abspath(filepath)  # absolute path
        file.save(filepath)
        print(f"🎧 File saved successfully at: {filepath}")

        # Split long audio into 60-sec chunks
        chunks = split_audio(filepath, chunk_length_ms=60000)

        # Transcribe each chunk and combine
        full_text = ""
        for chunk_file in chunks:
            try:
                result = model.transcribe(chunk_file)
                full_text += result["text"] + " "
            except Exception as e:
                print(f"❌ Error transcribing chunk {chunk_file}: {e}")

        full_text = full_text.strip()
        if not full_text:
            return jsonify({"error": "Audio could not be processed. Try a different file format or shorter file."}), 400

        # Summarization + keyword extraction
        summary = summarize_text(full_text)
        keywords = extract_keywords(full_text)

        return jsonify({
            "text": full_text,
            "summary": summary,
            "keywords": keywords
        })

    except Exception as e:
        print(f"❌ Internal error: {e}")
        return jsonify({"error": str(e)}), 500

# -------------------- Helper: Split audio --------------------
def split_audio(file_path, chunk_length_ms=60000):
    audio = AudioSegment.from_file(file_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i+chunk_length_ms]
        chunk_path = f"{file_path}_chunk{i//chunk_length_ms}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks

# -------------------- Summarization --------------------
def summarize_text(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, 2)  # 2 sentences
    return " ".join(str(sentence) for sentence in summary)

# -------------------- Keyword extraction --------------------
def extract_keywords(text):
    tokens = word_tokenize(text)
    words = [w.lower() for w in tokens if w.isalpha()]
    stop_words = set(stopwords.words('english'))
    filtered = [w for w in words if w not in stop_words]
    freq = {}
    for w in filtered:
        freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w[0] for w in sorted_words[:5]]

# -------------------- Run app --------------------
if __name__ == '__main__':
    app.run(debug=True)
