from flask import Flask, request, send_file, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL lipsa"}), 400

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '/tmp/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': '/usr/bin/ffmpeg',
            'quiet': True,
            'cookiefile': 'cookies.txt',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "audio")  
            mp3_path = f"/tmp/{title}.mp3"

        if not os.path.exists(mp3_path):
            return jsonify({"error": "Fișierul mp3 nu a fost creat"}), 500

        return send_file(mp3_path, as_attachment=True, download_name=f"{title}.mp3")

    except Exception as e:
        return jsonify({"error": str(e)}), 500 
