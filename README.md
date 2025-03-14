# YouTube HD Downloader (Flask + yt-dlp)

This project is a web application built using **Flask** and **yt-dlp** that allows users to download YouTube videos in high definition (up to 1080p) with merged audio. The app downloads the best quality video and audio, then merges them into a single **MP4** file using **ffmpeg**.

---

## Features

- **Download YouTube videos** in the best available quality (up to 1080p).
- **Audio and video streams** are merged into one file (MP4).
- **Simple, user-friendly interface** to input the video URL.
- **Status updates** on the download process, including progress bars.

---

## Technology Stack

- **Backend**: Flask (Python Web Framework)
- **Video Downloader**: yt-dlp (YouTube video downloader)
- **Video Processing**: ffmpeg (For merging video and audio streams)
- **Frontend**: HTML, CSS (UI)
- **Deployment**: Docker (For containerized deployment)

---

## Requirements

To run the project locally, you need the following dependencies:

- **Python 3.x**
- **Flask**: Python web framework
- **yt-dlp**: A powerful tool for downloading videos from YouTube and other platforms.
- **ffmpeg**: A multimedia framework for handling video, audio, and other multimedia files and streams.

### Installing FFmpeg

For FFmpeg to work properly with this application, you need to install it on your system. FFmpeg is required to merge the video and audio streams into a single MP4 file.

Please view the following video for detailed instructions on how to install FFmpeg on your system:

[How to Install FFmpeg](https://www.youtube.com/watch?v=JR36oH35Fgg)

---

### Origin of the Project

The reason I developed this project is quite personal. I needed to download a YouTube course in 1080p, but YouTube only provided the video in 360p. Frustrated with the lack of quality options, I decided to create this solution to easily download YouTube videos in higher quality (up to 1080p), with merged audio and video, for better learning and offline viewing.

---

### Usage

1. Clone or download this repository.
2. Install the required dependencies using the following command:

```bash
pip install -r requirements.txt
