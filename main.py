import yt_dlp
import argparse
import os
import sys
from datetime import datetime, timedelta
import json

CHANNELS = [
    'https://www.youtube.com/example',
]

DOWNLOAD_PATH = 'C:/example'
DEBUG = "OFF"

def debug(text):
    '''
    Allows to print additional information if errors persist
    '''
    if DEBUG == "ON":
        print(text)

def get_videos(channels, days=3):
    videos = []
    opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'playlistend': 10
    }

    # create custom cutoff
    cutoff = datetime.now() - timedelta(days=days) if days else None

    with yt_dlp.YoutubeDL(opts) as ydl:
        for channel in channels:
            # catch errors
            try:
                # extract info from selected channel, do not download
                info = ydl.extract_info(channel, download=False)
                for entry in info.get('entries', []):
                    # if date cutoff has been created obtain upload data in order to filter videos
                    if cutoff:
                        upload_date = entry.get('upload_date')
                        if upload_date:
                            video_date = datetime.strptime(upload_date, '%Y%m%d')
                            if video_date < cutoff:
                                continue
                    # get channel name straight from url
                    channel_name = channel.split("/", 4)[3]
                    # prepare data to save
                    videos.append({
                        'id': entry['id'],
                        'title': entry.get('title', 'Unknown'),
                        'url': entry['url'],
                        'uploader': channel_name
                    })
            except Exception as e:
                print(f"Error processing {channel}: {e}")

    return videos


def build_format(quality=None, audio_only=False, audio_codec='aac', audio_quality='320'):
    '''
    Creates a command for yt-dlp based on given parameters

    Arguments:
        quality (str): Video quality. Examples: '480', '720', '1080'. Note that it should be used without 'p'
        audio_only (bool): Saves only audio, without video
        audio_codec (str): Selects audio codec to be used for downloaded audio
        audio_quality (str): Selects audio quality in kbps. Examples: '320', '256', '128'

    Returns:
        A command (string) with selected arguments
        or 'best', which means to save best video and best audio quality.
    '''
    if audio_only:
        return f'bestaudio[acodec={audio_codec}]/bestaudio'

    if quality:
        return f'best[height<={quality}]/best'

    return 'best'


def file_exists(video_id, title, download_path, audio_only=False):
    '''
    Checks if file that user wants to download already exists in selected folder
    '''
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    ext = 'm4a' if audio_only else 'mkv'
    filename = f"{safe_title} [{video_id}].{ext}"
    return os.path.exists(os.path.join(download_path, filename))


def download_videos(videos, quality=None, audio_only=False, audio_codec='aac', audio_quality='320'):
    '''
    Downloads fetched videos based on functions used before.
    Videos are taken from global list at the beginning of the code.
    '''
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)

    opts = {
        'format': build_format(quality, audio_only, audio_codec, audio_quality),
        'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s [%(id)s].%(ext)s'),
        'writeinfojson': False,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'ignoreerrors': True
    }

    if audio_only:
        opts.update({
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_codec,
                'preferredquality': audio_quality,
            }]
        })

    with yt_dlp.YoutubeDL(opts) as ydl:
        # for each video check if it was already saved and if not - try to download it
        for video in videos:
            if file_exists(video['id'], video['title'], DOWNLOAD_PATH, audio_only):
                debug(f"Skipping {video['title']} - already exists")
                continue

            try:
                ydl.download([video['url']])
                print(f"Downloaded: {video['title']}")
            except Exception as e:
                print(f"Error downloading {video['title']}: {e}")


def download_single(url, quality=None, audio_only=False, audio_codec='aac', audio_quality='320'):
    '''
    Additional option to save a single video from provided url
    '''
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)

    opts = {
        'format': build_format(quality, audio_only, audio_codec, audio_quality),
        'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s [%(id)s].%(ext)s'),
        'writeinfojson': False,
        'writesubtitles': False,
        'writeautomaticsub': False
    }

    if audio_only:
        opts.update({
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_codec,
                'preferredquality': audio_quality,
            }]
        })

    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if file_exists(info['id'], info['title'], DOWNLOAD_PATH, audio_only):
                print(f"File already exists: {info['title']}")
                return

            ydl.download([url])
            print(f"Downloaded: {info['title']}")
        except Exception as e:
            print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fetch', action='store_true', help='Fetch video info only')
    parser.add_argument('--download', action='store_true', help='Download videos from channels')
    parser.add_argument('--single', help='Download single video from URL')
    parser.add_argument('--days', type=int, help='Filter videos from last X days')
    parser.add_argument('--q', type=int, help='Maximum quality (e.g., 720 for 720p)')
    parser.add_argument('--audio_only', action='store_true', help='Download audio only')
    parser.add_argument('--audio_codec', default='aac', help='Audio codec (default: aac)')
    parser.add_argument('--audio_quality', default='320', help='Audio quality in kbps (default: 320)')

    args = parser.parse_args()

    if args.single:
        download_single(args.single, args.q, args.audio_only, args.audio_codec, args.audio_quality)
    elif args.fetch:
        videos = get_videos(CHANNELS, args.days)
        for v in videos:
            print(f"{v['uploader']}: {v['title']} ({v['id']})")

        with open('videos.json', 'w') as f:
            json.dump(videos, f)
        print(f"\nFound {len(videos)} videos. Saved to videos.json")
    elif args.download:
        if os.path.exists('videos.json'):
            with open('videos.json', 'r') as f:
                videos = json.load(f)
        else:
            videos = get_videos(CHANNELS, args.days)

        download_videos(videos, args.q, args.audio_only, args.audio_codec, args.audio_quality)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
