# Django imports
from django.db import models
from django.contrib.auth import get_user_model


# database for a user's playlists
class Playlist(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, related_name='playlists')


# database for songs in playlists
class PlaylistSong(models.Model):
    spotify_id = models.CharField(max_length=200)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, null=True, related_name='songs')


# database for uris of songs the user has listened to
class ListenHistorySong(models.Model):
    spotify_id = models.CharField(max_length=200)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, related_name='listen_history_songs')
