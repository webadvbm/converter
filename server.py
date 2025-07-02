from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import re

app = Flask(__name__)

def sanitize_filename(name):
    # Scoate caractere ilegale din nume de fișier
    return re.sub(r'[\\/*?:"<>|]', "", name)

@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json()
    url = data.get("url")
    format_requested = data.get("format", "mp3").lower()  # mp3 sau mp4
    if not url:
        return jsonify({"error": "URL lipsă"}), 400

    if format_requested not in ("mp3", "mp4"):
        return jsonify({"error": "Format necunoscut"}), 400

    try:
        output_template = "/tmp/%(title)s.%(ext)s"

        ydl_opts = {
            'format': 'bestaudio/best' if format_requested == "mp3" else 'bestvideo+bestaudio/best',
            'outtmpl': output_template,
            'quiet': True,
            'cookiefile': 'cookies.txt',  # asigură-te că există în container
            'postprocessors': [],
        }

        if format_requested == "mp3":
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "file")
            sanitized_title = sanitize_filename(title)
            extension = "mp3" if format_requested == "mp3" else info.get("ext", "mp4")
            file_path = f"/tmp/{sanitized_title}.{extension}"

        if not os.path.exists(file_path):
            return jsonify({"error": f"Fișierul {file_path} nu a fost creat"}), 500

        return send_file(file_path, as_attachment=True, download_name=f"{sanitized_title}.{extension}")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
