from flask import Flask, request, send_file, jsonify, Response
from urllib.parse import quote
import yt_dlp
import os
import uuid
import traceback

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL missing'}), 400

    output_dir = '/tmp'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Template pentru numele fi╚Öierului (doar titlul video)
    outtmpl = os.path.join(output_dir, '%(title)s.%(ext)s')

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
         'ffmpeg_location': '/usr/bin/ffmpeg',
        'no_warnings': True,
        'forcefilename': True,
        'cookiefile': 'cookies.txt',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Descarc audio de la URL: {url}")
            info = ydl.extract_info(url, download=True)

        # Preg─âtim numele fi╚Öierului mp3
        filename = ydl.prepare_filename(info)
        mp3_file = os.path.splitext(filename)[0] + '.mp3'

        if not os.path.isfile(mp3_file):
            return jsonify({'error': 'MP3 file not found after conversion'}), 500

        print(f"Trimit fiserul: {mp3_file}")

        file_name_only = os.path.basename(mp3_file)

        response = send_file(mp3_file, as_attachment=True)
        filename_encoded = quote(file_name_only)
        response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{filename_encoded}"
        return response

    except Exception as e:
        print("EROARE LA DESCARCARE:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 
