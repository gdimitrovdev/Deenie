import random
import os

from dotenv import load_dotenv
import spotipy
from youtubesearchpython import VideosSearch
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate

from app.models import Playlist, PlaylistSong
from app.forms import PlaylistForm, SearchForm


load_dotenv()

SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')

client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, 
    client_secret=SPOTIPY_CLIENT_SECRET
)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


@login_required
def index(request):
    # get current user's playlists from database
    playlists = request.user.playlists.all()
    # form for creating playlists
    playlist_form = PlaylistForm()
    # form for searching
    search_form = SearchForm()

    # generate random album to recommend to the user
    new_album_releases = spotify.new_releases(limit=50)['albums']['items']
    random_album = random.choice(new_album_releases)

    album_info = {
        'name': random_album['name'],
        'id': random_album['id'],
        'artist': ', '.join(artist['name'] for artist in random_album['artists']),
        'artist_id': random_album['artists'][0]['id'],
        'cover': random_album['images'][0]['url'],
    }

    # get the user's name
    username = request.user

    # # find recommended songs for the user
    # uris = request.user.uris.all()
    # uris = [uri.uri for uri in uris]

    # if len(uris) > 0:
    #     recommended_tracks = spotify.recommendations(seed_tracks=uris, limit=3)['tracks']
    #     recommended_tracks_names = []
    #     recommended_tracks_artists = []
    #     recommended_tracks_pictures = []
    #     recommended_tracks_albums = []
    #     for i in range(3):
    #         recommended_tracks_names.append(recommended_tracks[i]['name'])
    #         recommended_tracks_artists.append(recommended_tracks[i]['artists'][0]['name'])
    #         recommended_tracks_pictures.append(recommended_tracks[i]['album']['images'][0]['url'])
    #         recommended_tracks_albums.append(recommended_tracks[i]['album']['name'])
    #     recommended_zip = zip(recommended_tracks_names, recommended_tracks_artists, recommended_tracks_pictures, recommended_tracks_albums)
    #     is_found = True
    # else:
    #     recommended_zip = []
    #     is_found = False

    context = {
        'playlists': playlists,
        'playlist_form': playlist_form,
        'search_form': search_form,
        'album_info': album_info,
        'username': username,
        # 'uris': uris,
        # 'zip': recommended_zip,
        # 'is_found': is_found,
    }
    return render(request, 'app/index.html', context)


def register(request):
    # get the registration form
    form = UserCreationForm()

    # register a new user
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')

    context = {
        'form': form
    }
    return render(request, 'registration/register.html', context)


def add(request):
    # get the form for creating new playlist
    playlist_form = PlaylistForm()

    # create the new playlist
    if request.method == 'POST':
        playlist_form = PlaylistForm(request.POST)
        if playlist_form.is_valid():
            new_playlist = Playlist(name=request.POST['name'], user=request.user)
            new_playlist.save()

    return redirect('../')


def delete(request, playlist_id):
    # delete playlist by id
    playlist=request.user.playlists.get(pk=playlist_id)
    playlist.delete()

    return redirect('../../')


def playlist(request, playlist_id):
    # get the search form
    search_form=SearchForm()

    # get the playlist and show it's songs
    playlist=request.user.playlists.get(pk=playlist_id)
    songs=playlist.songs.all()

    context={'songs':songs, 'playlist':playlist, 'search_form':search_form}
    return render(request, 'app/playlist.html',context)


def search(request):
    song_results = []
    album_results = []
    artist_results = []

    if request.method == 'POST':
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            keyword = request.POST['keyword']
            song_search_results = spotify.search(q=keyword, type='track', limit=5)
            album_search_results = spotify.search(q=keyword, type='album', limit=5)
            artist_search_results = spotify.search(q=keyword, type='artist', limit=5)

            if 'tracks' in song_search_results:
                for song in song_search_results['tracks']['items']:
                    song_result = {
                        'id': song['id'],
                        'name': song['name'],
                        'cover': song['album']['images'][0]['url'],
                    }

                    song_results.append(song_result)

            if 'albums' in album_search_results:
                for album in album_search_results['albums']['items']:
                    album_result = {
                        'id': album['id'],
                        'name': album['name'],
                        'cover': album['images'][0]['url'],
                    }

                    album_results.append(album_result)

            if 'artists' in artist_search_results:
                for artist in artist_search_results['artists']['items']:
                    artist_result = {
                        'id': artist['id'],
                        'name': artist['name'],
                        'picture': album['images'][0]['url'],
                    }

                    artist_results.append(artist_result)
        
    else:
        return redirect('/')

    context = {
        'songs': song_results,
        'albums': album_results,
        'artists': artist_results,
        'search_form': search_form,
    }
    return render(request, 'app/search.html', context)


def select(request, id, title):
    # select playlist to add current song to
    playlists=request.user.playlists.all()
    form=SearchForm()
    context={'playlists':playlists, 'id':id, 'title':title, 'search_form':form}
    return render(request, 'app/select.html', context)


def addtopl(request, playlist_id, song_id, title):
    # add song to selected playlist
    playlist_selected = request.user.playlists.get(pk=playlist_id)
    song = PlaylistSong(spotify_id=song_id, playlist=playlist_selected)
    song.save()
    return redirect('/')


def removefrompl(request, playlist_id, song_id):
    # remove song from playlist
    playlistSelected=request.user.playlists.get(pk=playlist_id)
    songToDel=playlistSelected.songs.get(pk=song_id)
    songToDel.delete()
    return redirect('../../../playlist/'+str(playlist_id))


# render a page for the selected song
def song(request, id):
    search_form = SearchForm()

    song_result = spotify.track(id)

    audio_url = ''

    youtube_result = VideosSearch(song_result['name'], limit=1).result()
    if youtube_result['result']:
        video_url = youtube_result['result'][0]['link']
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            audio_url = info['url']

    song = {
        'id': id,
        'name': song_result['name'],
        'audio_url': audio_url,
        'cover': song_result['album']['images'][0]['url'],
        'artist': ', '.join(artist['name'] for artist in song_result['artists']),
        'artist_id': song_result['artists'][0]['id'],
    }

    # find similar artists to the current one
    # artist_uri = spotify.track(song_uri)['album']['artists'][0]['uri']
    # artist = spotify.artist(artist_uri)['name']
    # similar_artists = []
    # pictures=[]
    # endofrow=[]
    # image=track['album']['images'][1]['url']
    # for i in range(5):
    #     similar_artists.append(spotify.artist_related_artists(artist_uri)['artists'][i]['name'])
    #     pictures.append(spotify.artist_related_artists(artist_uri)['artists'][i]['images'][2]['url'])
    #     if i==1 or i==4:
    #         endofrow.append(True)
    #     else:
    #         endofrow.append(False)
    # real_title=track['name']
    # artists=zip(similar_artists,pictures,endofrow)
    # new_uri=URIs(uri=song_uri, user=request.user)
    # new_uri.save()
    # isfound=True

    context = {
        'song': song,
        'search_form': search_form,
    }
    return render(request, 'app/song.html', context)


# a function that allows us to refresh the current page
# it is used to find new random album for the user
def refresh(request):
    return redirect('/')


def album(request, id):
    album_result = spotify.album(id)

    album_info = {
        'name': album_result['name'],
        'cover': album_result['images'][0]['url'],
        'artist': ', '.join(artist['name'] for artist in album_result['artists']),
        'artist_id': album_result['artists'][0]['id'],
    }

    track_results = spotify.album_tracks(id)['items']
    tracks = []

    for track_result in track_results:
        track = {
            'name': track_result['name'],
            'id': track_result['id'],
        }

        tracks.append(track)

    # find similar artists to the album artist
    # artist_uri = results['albums']['items'][0]['artists'][0]['uri']
    # similar_artists = []
    # similar_names=[]
    # forbidden = []
    # albums = []
    # for i in range(3):
    #     index = random.randint(0, 4)
    #     while index in forbidden:
    #         index = random.randint(0, 4)
    #     similar_artists.append(spotify.artist_related_artists(artist_uri)['artists'][index]['uri'])
    #     similar_names.append(spotify.artist_related_artists(artist_uri)['artists'][index]['name'])
    #     forbidden.append(index)

    # get random albums from the similar artists and recommend them to the user
    # for i in similar_artists:
    #     index = random.randint(0, len(spotify.artist_albums(i)['items'])-1)
    #     albums.append(spotify.artist_albums(i)['items'][index]['name'])
    #     similar_pictures.append(spotify.artist_albums(i)['items'][index]['images'][1]['url'])

    search_form = SearchForm()

    context = {
        'album': album_info,
        'tracks': tracks,
        'search_form': search_form,
        # 'similar':zip(albums,similar_pictures,similar_names)
    }
    return render(request, 'app/album.html', context)


def artist(request, id):
    search_form = SearchForm()

    # get the artist
    artist_result = spotify.artist(id)

    # get details about the artist
    artist_info = {
        'name': artist_result['name'],
        'popularity': artist_result['popularity'],
        'image': artist_result['images'][0]['url'],
        'followers': artist_result['followers']['total'],
        'genres': artist_result['genres'][:3],
    }

    # get artist's  albums
    album_results = spotify.artist_albums(id, limit=50)['items']
    albums = [
        {
            'name': album['name'],
            'cover': album['images'][0]['url'],
            'id': album['id'],
        } for album in album_results
    ]

    # # get similar artists
    # similar_artists_result = spotify.artist_related_artists(id)['artists'][:3]
    # similar_artists = [
    #     {
    #         'id': artist['id'],
    #         'name': artist['name'],
    #         'image': artist['images'][0]['url']
    #     } for artist in similar_artists_result
    # ]

    context = {
        'search_form': search_form,
        'artist_info': artist_info,
        'albums': albums,
        # 'similar_artists': similar_artists,
    }
    return render(request, 'app/artist.html', context)
