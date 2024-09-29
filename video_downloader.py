import os
import subprocess
import requests
from bs4 import BeautifulSoup
import yt_dlp

# Function to update yt-dlp automatically
def update_yt_dlp():
    try:
        subprocess.run(['pip', 'install', '--upgrade', 'yt-dlp'], check=True)
        print("yt-dlp has been updated to the latest version.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to update yt-dlp: {e}")

# Function to download videos using yt-dlp
def download_video_with_ytdlp(video_url, output_path):
    try:
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),  # Output file template
            'format': 'bestvideo+bestaudio/best',  # Best overall quality
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',  # Convert to mp4 format
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading video from {video_url}...")
            ydl.download([video_url])
            print(f"Video downloaded successfully and saved to {output_path}")
    except Exception as e:
        print(f"Error downloading video with yt-dlp: {e}")

# Backup function to handle TikTok via scraping if yt-dlp fails
def download_tiktok_fallback(video_url, output_path):
    try:
        response = requests.get(video_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        video_tag = soup.find('video')

        if video_tag:
            video_src = video_tag.get('src')
            video_content = requests.get(video_src).content

            output_file = os.path.join(output_path, 'tiktok_video.mp4')
            with open(output_file, 'wb') as f:
                f.write(video_content)
            print(f"TikTok video downloaded successfully and saved to {output_file}")
        else:
            print("Unable to find the video in the page source.")
    except Exception as e:
        print(f"Error downloading TikTok video (fallback method): {e}")

# Main function to handle multiple platforms
def download_video(video_url, output_path):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Check if it's a YouTube, TikTok, or other platform URL
    if "youtube.com" in video_url or "youtu.be" in video_url:
        download_video_with_ytdlp(video_url, output_path)
    elif "tiktok.com" in video_url:
        try:
            download_video_with_ytdlp(video_url, output_path)
        except Exception as e:
            print(f"Error downloading from TikTok via yt-dlp: {e}")
            print("Attempting fallback download method...")
            download_tiktok_fallback(video_url, output_path)
    else:
        # Use yt-dlp for all other platforms
        download_video_with_ytdlp(video_url, output_path)

if __name__ == "__main__":
    # Auto-update yt-dlp to the latest version
    update_yt_dlp()

    video_url = input("Enter the video URL: ").strip()
    output_path = input("Enter the output folder path: ").strip()

    download_video(video_url, output_path)
