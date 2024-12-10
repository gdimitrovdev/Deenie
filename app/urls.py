# Django imports
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('add/', views.add, name='add'),
    path('delete/<playlist_id>', views.delete, name='delete'),
    path('playlist/<playlist_id>', views.playlist, name='playlist'),
    path('search/', views.search, name='search'),
    path('select/<id>/<path:title>', views.select, name='select'),
    path('addtopl/<playlist_id>/<path:id>/<path:title>', views.addtopl, name='addtopl'),
    path('removefrompl/<playlist_id>/<path:song_id>', views.removefrompl, name='removefrompl'),
    path('more/<song_url>/<path:title>', views.more, name='more'),
    path('refresh/', views.refresh, name='refresh'),
    path('album/<path:album_name>/<path:artist_name>',views.album,name='album'),
    path('artist/<path:name>', views.artist, name='artist'),
]