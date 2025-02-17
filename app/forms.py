# Django imports
from django import forms


# form to create a new playlist
class PlaylistForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'playlist-form'}), max_length=200, label='')


# form to search for a song, artist or album
class SearchForm(forms.Form):
    keyword = forms.CharField(widget=forms.TextInput(attrs={'class': 'search', 'placeholder': 'Search'}), max_length=200, label='')
