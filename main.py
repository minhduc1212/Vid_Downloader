import os
import sys

# Ensure src module can be imported properly from command line
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.downloader import VideoDownloader

def main():
    output_folder = "Output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder, exist_ok=True)
        
    print("Welcome to the Universal Video Downloader!")
    print("Supported platforms: YouTube, Facebook, Instagram, TikTok, and more.")
    
    url = input("Enter the video URL: ").strip()
    if not url:
        print("No URL provided. Exiting.")
        return
        
    keep_raw = input("Keep raw audio/video files before merge? (y/N): ").strip().lower() == 'y'
        
    downloader = VideoDownloader(output_folder=output_folder, keep_raw_files=keep_raw)
    downloader.download_video(url)
    print(f"Done! Please check in the '{output_folder}' folder.")

if __name__ == "__main__":
    main()