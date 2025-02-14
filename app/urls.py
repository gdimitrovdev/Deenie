# Django imports
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('create-playlist/', views.create_playlist, name='create_playlist'),
    path('delete-playlist/<id>', views.delete_playlist, name='delete_playlist'),
    path('playlist/<id>', views.playlist, name='playlist'),
    path('search/', views.search, name='search'),
    path('add-to-playlist/', views.add_to_playlist, name='add_to_playlist'),
    path('remove-from-playlist/<song_id>/<playlist_id>', views.remove_from_playlist, name='remove_from_playlist'),
    path('song/<id>', views.song, name='song'),
    path('refresh/', views.refresh, name='refresh'),
    path('album/<id>', views.album, name='album'),
    path('artist/<id>', views.artist, name='artist'),
]