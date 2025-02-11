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
from django.views.decorators.csrf import csrf_exempt

from app.models import Playlist, Song, URIs
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
    form = PlaylistForm()
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
        'form': form,
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
    form=UserCreationForm()

    # register a new user
    if request.method=="POST":
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data['username']
            password=form.cleaned_data['password1']
            user=authenticate(username=username, password=password)
            login(request, user)
            return redirect('../')

    context = {
        'form': form
    }
    return render(request, 'registration/register.html', context)


def add(request):
    # get the form for creating new playlist
    form=PlaylistForm()

    #create the new playlist
    if request.method=="POST":
        form=PlaylistForm(request.POST)
        if form.is_valid():
            new_playlist=Playlist(text=request.POST['text'], user=request.user)
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
    # search youtube and spotify
    video_ids = []
    video_titles = []
    video_thumbnails = []
    pictureFound = []

    if request.method == 'POST':
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            # find youtube video for the keyword provided
            keyword = request.POST['keyword']
            results = VideosSearch(keyword, limit=3).result()['result']
            for i in range(len(results)):
                video_ids.append(results[i]['id'])
                video_titles.append(results[i]['title'])
                try:
                    video_thumbnails.append(results['result'][0]['thumbnails'][0]['url'])
                    pictureFound.append(True)
                except:
                    video_thumbnails.append('https://image.flaticon.com/icons/png/512/181/181668.png')
                    pictureFound.append(False)
            videos=zip(video_ids,video_titles,video_thumbnails, pictureFound)

            # search spotify for artists
            try:
                results = spotify.search(q='artist:' + keyword, type='artist')
                picture=results['artists']['items'][0]['images'][2]['url']
                name=results['artists']['items'][0]['name']
                artistFound=True
            except:
                picture=0
                name=0
                artistFound=False

            # search spotipy for albums
            try:
                results = spotify.search(q=keyword, type='album', limit=1)
                album_name=results['albums']['items'][0]['name']
                artist_name=results['albums']['items'][0]['artists'][0]['name']
                album_picture = results['albums']['items'][0]['images'][1]['url']
                albumFound=True
            except:
                artist_name = ''
                album_name=''
                album_picture=''
                albumFound=False

    context={'videos':videos,
             'search_form':search_form,
             'found':artistFound,
             'picture':picture,
             'name':name,
             'cover':album_picture,
             'album_name':album_name,
             'albumFound':albumFound,
             'artist_name':artist_name}
    return render(request, 'app/search.html', context)


def select(request, id, title):
    # select playlist to add current song to
    playlists=request.user.playlists.all()
    form=SearchForm()
    context={'playlists':playlists, 'id':id, 'title':title, 'search_form':form}
    return render(request, 'app/select.html', context)


def addtopl(request, playlist_id, id, title):
    # add song to selected playlist
    playlistSelected=request.user.playlists.get(pk=playlist_id)
    song=Song(url=id, playlist=playlistSelected, title=title)
    song.save()
    return redirect('../../../../')


def removefrompl(request, playlist_id, song_id):
    # remove song from playlist
    playlistSelected=request.user.playlists.get(pk=playlist_id)
    songToDel=playlistSelected.songs.get(pk=song_id)
    songToDel.delete()
    return redirect('../../../playlist/'+str(playlist_id))


# render a page for the selected song
@csrf_exempt
def more(request,song_url,title):
    # search spotify for details of the song (danceability, tempo etc.)
    try:
        ss = title
        ss=ss.split('ft.')
        ss=ss[0]
        if ss.__contains__('('):
            q = ss[0:ss.index('(')]
        elif ss.__contains__('['):
            q = ss[0:ss.index('[')]
        elif ss.__contains__('{'):
            q = ss[0:ss.index('{')]
        else:
            q = ss
        query = spotify.search(q, 1, 0, 'track')
        song_uri = query['tracks']['items'][0]['uri']
        track = spotify.track(song_uri)
        track_data = spotify.audio_features(song_uri)
        song_popularity = track['popularity']
        song_danceability = int(track_data[0]['danceability']*100)
        song_tempo = int(track_data[0]['tempo'])

        # find similar artists to the current one
        artist_uri = spotify.track(song_uri)['album']['artists'][0]['uri']
        artist = spotify.artist(artist_uri)['name']
        similar_artists = []
        pictures=[]
        endofrow=[]
        image=track['album']['images'][1]['url']
        for i in range(5):
            similar_artists.append(spotify.artist_related_artists(artist_uri)['artists'][i]['name'])
            pictures.append(spotify.artist_related_artists(artist_uri)['artists'][i]['images'][2]['url'])
            if i==1 or i==4:
                endofrow.append(True)
            else:
                endofrow.append(False)
        real_title=track['name']
        artists=zip(similar_artists,pictures,endofrow)
        new_uri=URIs(uri=song_uri, user=request.user)
        new_uri.save()
        isfound=True
    except:
        song_popularity="-"
        song_danceability ="-"
        song_tempo ="-"
        artist=''
        similar_artists=['','','','','']
        pictures=['','','','','']
        endofrow=['','','','','']
        artists = zip(similar_artists, pictures,endofrow)
        image=''
        real_title=title
        isfound=False

    '''
    If a user got to this page with an url of the song that is equal to 1, this means that instead of the youtube url we
    redirected to this function using argument 1.
    
    In the "albums" page we are redirecting to the "more" page using an url equal to one as it takes a lot of time to 
    find the url for every single song and this slows the site down. Instead we go to the more page and find the youtube
    url here.
    '''
    if song_url == '1':
        results1 = VideosSearch(title, limit=3).result()['result']
        song_url = results1[0]['id']
    search_form = SearchForm()
    url = 'https://www.youtube.com/watch?v=' + str(song_url)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
    }
    ydl = yt_dlp.YoutubeDL(ydl_opts)
    info = ydl.extract_info(song_url, download=False)
    audio_url = info['url']

    if image == '':
        image = results1[0]['thumbnails'][0]['url']

    # get all song details together
    details = {'popularity': song_popularity,
               'danceability': song_danceability,
               'tempo': song_tempo,
               'artist': artist,
               'artists': artists,
               'image': image,
               'isfound': isfound
               }

    context = {'url': song_url,
               'song_title': real_title,
               'details': details,
               'search_form': search_form,
               'real_url': audio_url,
               }
    return render(request, 'app/more.html', context)


# a function that allows us to refresh the current page
# it is used to find new random album for the user
def refresh(request):
    return redirect('../')


def album(request, id):
    album_result = spotify.album(id)

    album_info = {
        'name': album_result['name'],
        'cover': album_result['images'][0]['url'],
        'artist': ', '.join(artist['name'] for artist in album_result['artists']),
        'artist_id': album_result['artists'][0]['id'],
    }

    tracks_result = spotify.album_tracks(id)['items']
    tracks = []

    for i in range(len(tracks_result)):
        track = {
            'name': tracks_result[i]['name'],
            'id': tracks_result[i]['id'],
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
    albums_result = spotify.artist_albums(id, limit=50)['items']
    albums = [
        {
            'name': album['name'],
            'cover': album['images'][0]['url'],
            'id': album['id'],
        } for album in albums_result
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
