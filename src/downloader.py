import os
import yt_dlp
import requests
import re
import time
import json
import subprocess
import random

class VideoDownloader:
    def __init__(self, output_folder="Output", keep_raw_files=False):
        """
        Initialize the VideoDownloader.
        
        :param output_folder: The directory where downloaded videos will be saved.
        :param keep_raw_files: Whether to keep the raw audio and video files after merging.
        """
        self.output_folder = output_folder
        self.keep_raw_files = keep_raw_files

    def _get_ydl_opts(self, progress_callback=None):
        opts = {
            'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'),
            'keepvideo': self.keep_raw_files,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'quiet': False,
            'no_warnings': False,
        }
        if progress_callback:
            def hook(d):
                if d['status'] == 'downloading':
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    if total > 0:
                        pct = int(d.get('downloaded_bytes', 0) / total * 100)
                        progress_callback(pct)
            opts['progress_hooks'] = [hook]
        return opts

    def download_video(self, url, progress_callback=None):
        """
        Downloads a video from the given URL.
        Supports YouTube, Facebook, Instagram, TikTok, and many more.
        
        :param url: The URL of the video to download.
        :param progress_callback: Function to call with download percentage (0-100).
        """
        if "facebook.com" in url or "fb.watch" in url:
            self.download_facebook_video(url, progress_callback)
            return
            
        if "instagram.com" in url:
            self.download_instagram_video(url, progress_callback)
            return
        if "tiktok.com" in url:
            self.download_tiktok_video(url, progress_callback)
            return
        if "douyin.com" in url:
            self.download_douyin_video(url, progress_callback)
            return

        ydl_opts = self._get_ydl_opts(progress_callback)
        try:
            print(f"Downloading video from {url}...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            print(f"Failed to download video: {e}")

    def download_file(self, link, file_name, progress_callback=None):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
        }
        try:
            resp = requests.get(link, headers=headers, stream=True)
            resp.raise_for_status()
            total = int(resp.headers.get('content-length', 0))
            downloaded = 0
            with open(os.path.join(self.output_folder, file_name), 'wb') as f:
                for chunk in resp.iter_content(chunk_size=1024*64):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total and progress_callback:
                            progress_callback(int((downloaded / total) * 100))
        except Exception as e:
            print(f"Failed to download file {link}: {e}")

    def download_facebook_video(self, link, progress_callback=None):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Dnt': '1',
            'Dpr': '1.3125',
            'Priority': 'u=0, i',
            'Sec-Ch-Prefers-Color-Scheme': 'dark',
            'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'Sec-Ch-Ua-Full-Version-List': '"Chromium";v="124.0.6367.156", "Google Chrome";v="124.0.6367.156", "Not-A.Brand";v="99.0.0.0"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Model': '""',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Ch-Ua-Platform-Version': '"15.0.0"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Viewport-Width': '1463'
        }
        try:
            print(f"Fetching Facebook video info from {link}...")
            resp = requests.get(link, headers=headers)
            resp.raise_for_status()
            html = resp.text
        except Exception as e:
            print(f"Failed to open {link}: {e}")
            return

        # Extract video ID for naming
        video_id_match = re.search(r'(?:/videos/|/watch/\?v=|/reel/|/reels/|/posts/)([0-9]+)', resp.url)
        video_id = video_id_match.group(1) if video_id_match else str(int(time.time()))
        final_dest = os.path.join(self.output_folder, f'{video_id}.mp4')

        
        hd_match = re.search(r'"browser_native_hd_url":"([^"]+)"', html) or re.search(r'"playable_url_quality_hd":"([^"]+)"', html)
        sd_match = re.search(r'"browser_native_sd_url":"([^"]+)"', html) or re.search(r'"playable_url":"([^"]+)"', html)

        video_url = None
        if hd_match:
            video_url = json.loads(f'"{hd_match.group(1)}"')
            print("Found direct HD video URL.")
        elif sd_match:
            video_url = json.loads(f'"{sd_match.group(1)}"')
            print("Found direct SD video URL.")

        if video_url:
            print("Downloading direct video...")
            self.download_file(video_url, f'{video_id}.mp4', progress_callback)
            print(f"Successfully downloaded to {final_dest}")
            return

        dash_match = re.search(r'"dash_prefetch_experimental":\[([^\]]+)\]', html)
        if dash_match:
            try:
                sources = json.loads(f"[{dash_match.group(1)}]")
                if len(sources) >= 2:
                    video_rep, audio_rep = sources[0], sources[1]
                    
                    video_link_match = re.search(f'"representation_id":"{video_rep}"[\\s\\S]*?"base_url":"([^"]+)"', html)
                    audio_link_match = re.search(f'"representation_id":"{audio_rep}"[\\s\\S]*?"base_url":"([^"]+)"', html)
                    
                    if video_link_match and audio_link_match:
                        video_link = json.loads(f'"{video_link_match.group(1)}"')
                        audio_link = json.loads(f'"{audio_link_match.group(1)}"')
                        
                        print("Found DASH video and audio URLs. Downloading...")
                        self.download_file(video_link, 'video.mp4', progress_callback)
                        # Avoid double progress reporting by not passing callback to audio
                        self.download_file(audio_link, 'audio.mp4')
                        
                        video_path = os.path.join(self.output_folder, 'video.mp4')
                        audio_path = os.path.join(self.output_folder, 'audio.mp4')
                        
                        print("Merging files...")
                        cmd = f'ffmpeg -y -hide_banner -loglevel error -i "{video_path}" -i "{audio_path}" -c copy "{final_dest}"'
                        subprocess.call(cmd, shell=True)
                        
                        if not self.keep_raw_files:
                            if os.path.exists(video_path): os.remove(video_path)
                            if os.path.exists(audio_path): os.remove(audio_path)
                            
                        print(f"Successfully downloaded and merged to {final_dest}")
                        return
            except Exception as e:
                print(f"DASH extraction failed: {e}")

        print("Falling back to yt-dlp for Facebook video extraction...")
        ydl_opts = self._get_ydl_opts(progress_callback)
        ydl_opts['outtmpl'] = os.path.join(self.output_folder, f'{video_id}.%(ext)s')
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
        except Exception as e:
            print(f"yt-dlp failed to download Facebook video: {e}")

    def download_instagram_video(self, url, progress_callback=None):
        match = re.search(r'instagram\.com/(?:p|reel|tv)/([^/?#&]+)', url)
        if not match:
            print("Could not extract Instagram shortcode from URL.")
            return
            
        shortcode = match.group(1)
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
            'Referer': 'https://www.instagram.com/',
        })
        
        try:
            r = session.get('https://www.instagram.com/', timeout=10)
            csrf = session.cookies.get('csrftoken', domain='.instagram.com')
            if csrf:
                session.headers.update({'X-CSRFToken': csrf})
        except Exception as e:
            print(f"Failed to get csrftoken: {e}")

        sleep_time = random.uniform(3.0, 7.0)
        print(f"Waiting {sleep_time:.2f}s to avoid rate limiting...")
        time.sleep(sleep_time)
        
        doc_id = "8845758582119845"
        variables = json.dumps({
            "shortcode": shortcode,
            "fetch_tagged_user_count": None,
            "hoisted_comment_id": None,
            "hoisted_reply_id": None
        })

        query_url = "https://www.instagram.com/graphql/query"
        params = {"doc_id": doc_id, "variables": variables}

        print(f"Fetching Instagram video info for shortcode: {shortcode}...")
        try:
            response = session.get(query_url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                media = data.get('data', {}).get('xdt_shortcode_media')
                if media:
                    is_video = media.get('is_video', False)
                    video_url = media.get('video_url') if is_video else None
                    
                    if not is_video:
                        print("The provided Instagram link is not a video.")
                        return
                        
                    if video_url:
                        file_name = f"{shortcode}.mp4"
                        print("Found direct video URL. Downloading...")
                        self.download_file(video_url, file_name, progress_callback)
                        print(f"Successfully downloaded to {os.path.join(self.output_folder, file_name)}")
                        return
                else:
                    print("Could not find media in GraphQL response.")
        except Exception as e:
            print(f"GraphQL extraction failed: {e}")
            
        print("Falling back to yt-dlp for Instagram video extraction...")
        ydl_opts = self._get_ydl_opts(progress_callback)
        ydl_opts['outtmpl'] = os.path.join(self.output_folder, f'{shortcode}.%(ext)s')
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            print(f"yt-dlp failed to download Instagram video: {e}")

    def download_tiktok_video(self, url, progress_callback=None):
        ydl_opts = self._get_ydl_opts(progress_callback)
        try:
            print(f"Downloading TikTok video from {url}...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            print(f"Failed to download TikTok video: {e}")

    def download_douyin_video(self, url, progress_callback=None):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("Playwright is not installed. Falling back to yt-dlp...")
            ydl_opts = self._get_ydl_opts(progress_callback)
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as e:
                print(f"yt-dlp failed to download Douyin video: {e}")
            return

        user_data_dir = "./douyin_profile"
        print(f"Fetching Douyin video info from {url}...")

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
                viewport={'width': 1280, 'height': 720}
            )
            
            page = context.new_page()
            page.set_default_timeout(60000)

            result = {"full_mp4": None}

            def handle_response(response):
                if "aweme/v1/web/aweme/detail" in response.url:
                    try:
                        json_data = response.json()
                        play_addr = json_data['aweme_detail']['video']['play_addr']['url_list'][0]
                        result["full_mp4"] = play_addr.replace("http://", "https://")
                        print(f"Found Douyin direct video URL: {result['full_mp4'][:80]}...")
                    except Exception:
                        pass

            page.on("response", handle_response)
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                for _ in range(20): 
                    if result["full_mp4"]:
                        break
                    page.wait_for_timeout(500)
            except Exception as e:
                if not result["full_mp4"]:
                    print(f"Timeout or error extracting Douyin video link: {e}")

            video_url = result.get("full_mp4")
            context.close()

        if video_url:
            video_id_match = re.search(r'/video/(\d+)', url)
            video_id = video_id_match.group(1) if video_id_match else str(int(time.time()))
            file_name = f"douyin_{video_id}.mp4"
            
            print("Downloading Douyin video...")
            # We take advantage of the class' built-in chunked downloader
            self.download_file(video_url, file_name, progress_callback)
            print(f"Successfully downloaded to {os.path.join(self.output_folder, file_name)}")
        else:
            print("Could not find Douyin video URL. Falling back to yt-dlp...")
            ydl_opts = self._get_ydl_opts(progress_callback)
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as e:
                print(f"yt-dlp failed to download Douyin video: {e}")