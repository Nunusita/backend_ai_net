from flask import Flask, request, jsonify
import os
import yt_dlp
import whisper
import moviepy.editor as mp
import uuid
import tempfile
from deep_translator import GoogleTranslator

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Backend AI Net funcionando con subtítulos en español."

@app.route('/process', methods=['POST'])
def process_video():
    try:
        data = request.get_json()
        url = data.get("url")
        target_lang = data.get("lang", "es")  # Idioma destino, por defecto español

        if not url:
            return jsonify({"error": "Falta el enlace del video."}), 400

        # Crear carpeta temporal para guardar video
        temp_dir = tempfile.mkdtemp()
        video_path = os.path.join(temp_dir, f"{uuid.uuid4()}.mp4")

        # Descargar video
        ydl_opts = {
            'format': 'best',
            'outtmpl': video_path,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Cargar modelo Whisper
        model = whisper.load_model("base")
        result = model.transcribe(video_path)

        transcript = result["text"]

        # Traducir subtítulos si se solicita idioma distinto
        if target_lang != "original":
            translated = GoogleTranslator(source='auto', target=target_lang).translate(transcript)
        else:
            translated = transcript

        return jsonify({
            "status": "ok",
            "original_transcript": transcript,
            "translated_subtitles": translated,
            "language": target_lang
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
