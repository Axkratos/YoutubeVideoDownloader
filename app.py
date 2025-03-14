from flask import Flask, render_template_string, request, jsonify, send_file, after_this_request
import yt_dlp
import os
import subprocess
import logging
import time

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube HD Downloader</title>
    <style>
        :root {
            --primary: #2c3e50;
            --accent: #e74c3c;
            --light: #ecf0f1;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f6fa;
            margin: 0;
            padding: 2rem;
        }
        
        .container {
            max-width: 800px;
            margin: 2rem auto;
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        h1 {
            color: var(--primary);
            margin-bottom: 2rem;
            font-size: 2.5rem;
        }
        
        .input-group {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        input {
            flex: 1;
            padding: 1rem;
            border: 2px solid #dfe6e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        input:focus {
            border-color: var(--accent);
            outline: none;
            box-shadow: 0 0 0 3px rgba(231,76,60,0.1);
        }
        
        button {
            padding: 1rem 2rem;
            background: var(--accent);
            border: none;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, background 0.3s;
        }
        
        button:hover {
            background: #c0392b;
            transform: translateY(-2px);
        }
        
        #status {
            margin: 1.5rem 0;
            padding: 1rem;
            border-radius: 8px;
            background: #f8f9fa;
            min-height: 20px;
        }
        
        .progress {
            height: 8px;
            background: #dfe6e9;
            border-radius: 4px;
            overflow: hidden;
            margin: 1rem 0;
        }
        
        .progress-bar {
            height: 100%;
            background: var(--accent);
            width: 0;
            transition: width 0.3s ease;
        }
        
        #download-link a {
            display: inline-block;
            margin-top: 1rem;
            padding: 1rem 2rem;
            background: #27ae60;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: background 0.3s;
        }
        
        #download-link a:hover {
            background: #219a52;
        }
        
        .loader {
            display: none;
            border: 4px solid #f3f3f3;
            border-top: 4px solid var(--accent);
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 1rem auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>YouTube HD Downloader</h1>
        <div class="input-group">
            <input type="text" id="url" placeholder="Paste YouTube URL here...">
            <button onclick="startDownload()">Download HD</button>
        </div>
        <div class="progress">
            <div class="progress-bar" id="progressBar"></div>
        </div>
        <div id="status">Ready to download</div>
        <div class="loader" id="loader"></div>
        <div id="download-link"></div>
    </div>

    <script>
        function updateUI(status, progress = 0) {
            const statusEl = document.getElementById('status');
            const progressBar = document.getElementById('progressBar');
            const loader = document.getElementById('loader');
            
            statusEl.textContent = status;
            progressBar.style.width = `${progress}%`;
            
            if(progress > 0 && progress < 100) {
                loader.style.display = 'block';
            } else {
                loader.style.display = 'none';
            }
        }

        function startDownload() {
            const url = document.getElementById('url').value;
            if (!url) return alert('Please enter a YouTube URL');

            updateUI('Starting download...', 10);
            
            fetch('/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) throw data.error;
                
                updateUI('Processing video...', 90);
                const downloadLink = document.getElementById('download-link');
                
                // Create temporary iframe for download
                const iframe = document.createElement('iframe');
                iframe.style.display = 'none';
                iframe.src = `/get_video/${data.filename}`;
                document.body.appendChild(iframe);
                
                updateUI('Download complete!', 100);
                downloadLink.innerHTML = `
                    <a href="/get_video/${data.filename}" download>
                        Click to Download Again
                    </a>
                `;
                
                // Cleanup after 10 seconds
                setTimeout(() => {
                    downloadLink.innerHTML = '';
                    updateUI('Ready to download');
                }, 10000);
            })
            .catch(error => {
                updateUI(`Error: ${error}`, 0);
            });
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/download", methods=["POST"])
def download_video():
    data = request.json
    url = data.get("url")
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        ydl_opts = {
            'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename = os.path.basename(filename).replace('.webm', '.mp4')

        # Convert audio to AAC with proper stream mapping
        output_filename = f"converted_{int(time.time())}_{filename}"
        output_path = os.path.join(DOWNLOAD_FOLDER, output_filename)

        ffmpeg_cmd = [
            'ffmpeg', '-y', '-i', os.path.join(DOWNLOAD_FOLDER, filename),
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-map', '0',
            '-movflags', '+faststart',
            output_path
        ]

        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        os.remove(os.path.join(DOWNLOAD_FOLDER, filename))

        return jsonify({"filename": output_filename})

    except subprocess.CalledProcessError as e:
        app.logger.error(f"FFmpeg Error: {e.stderr.decode()}")
        return jsonify({"error": f"Video processing failed: {e.stderr.decode()}"}), 500
        
    except Exception as e:
        app.logger.error(f"Download Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/get_video/<filename>")
def get_video(filename):
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        @after_this_request
        def cleanup(response):
            try:
                os.remove(filepath)
            except Exception as e:
                app.logger.error(f"Cleanup Error: {str(e)}")
            return response
        return send_file(filepath, as_attachment=True)
    return "File not found", 404

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
