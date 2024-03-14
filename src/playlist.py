import os
import isodate
import datetime

from googleapiclient.discovery import build


api_key: str = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=api_key)


class PlayList:

    def __init__(self, playlist_id):
        self.playlist_id = playlist_id
        self.playlist_videos = youtube.playlistItems().list(playlistId=playlist_id,
                                               part='contentDetails',
                                               maxResults=50,
                                               ).execute()
        self.video_ids = [video['contentDetails']['videoId'] for video in self.playlist_videos['items']]
        response = youtube.playlists().list(id=playlist_id,
                                                      part='snippet',
                                                      ).execute()
        self.title = response['items'][0]['snippet']['title']
        self.url = f"https://www.youtube.com/playlist?list={playlist_id}"

    @property
    def total_duration(self):
        video_response = youtube.videos().list(part='contentDetails,statistics',
                                       id=','.join(self.video_ids)
                                       ).execute()

        duration = datetime.timedelta(0,0,0)
        for video in video_response['items']:
            iso_8601_duration = video['contentDetails']['duration']
            duration_video = isodate.parse_duration(iso_8601_duration)
            duration = duration + duration_video
        return duration

    def show_best_video(self):
        playlist_videos = youtube.playlistItems().list(playlistId=self.playlist_id,
                                                       part='contentDetails',
                                                       maxResults=50,
                                                       ).execute()
        like_count = 0
        for video in playlist_videos["items"]:
            video_response = youtube.videos().list(part='snippet,statistics,contentDetails,topicDetails',
                                                   id=video["contentDetails"]["videoId"]
                                                   ).execute()
            if like_count < int(video_response['items'][0]['statistics']['likeCount']):
                like_count = int(video_response['items'][0]['statistics']['likeCount'])
                best_video_url = f"https://youtu.be/{video["contentDetails"]["videoId"]}"
        return best_video_url
