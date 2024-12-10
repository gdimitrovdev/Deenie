# Django imports
from django.db import models
from django.contrib.auth import get_user_model

# database for a user's playlists
class Playlist(models.Model):
    text=models.CharField(max_length=200)
    user=models.ForeignKey(get_user_model(),on_delete=models.CASCADE,null=True,related_name='playlists')
    selected=models.BooleanField(default=False)

# database for songs in playlists
class Song(models.Model):
    url=models.CharField(max_length=200)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, null=True, related_name='songs')
    title=models.CharField(max_length=200)

# database for uris of songs the user has listened to
class URIs(models.Model):
    uri=models.CharField(max_length=200)
    user=models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, related_name='uris')