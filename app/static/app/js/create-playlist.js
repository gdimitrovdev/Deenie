document.getElementById('playlist-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response error');
        return response.json();
    })
    .then(data => {
        if (data.playlist) {
            const playlist = data.playlist;
            const table = document.querySelector('.playlists-table');
            
            // Create new table row
            const newRow = document.createElement('tr');
            newRow.setAttribute("id", `playlist-row-${playlist.id}`);

            const urlPlaylist = playlistUrlMasked.replace('maskstring', playlist.id);
            const urlDeletePlaylist = deletePlaylistUrlMasked.replace('maskstring', playlist.id);

            newRow.innerHTML = `
                <td class="td1">
                    <a href="${urlPlaylist}">${playlist.name}</a>
                </td>
                <td>
                    <a class="new-delete-playlist-button" href="${urlDeletePlaylist}">Delete playlist</a>
                </td>
            `;
            
            table.insertAdjacentElement('afterbegin', newRow);

            addDeleteListener(document.getElementsByClassName("new-delete-playlist-button")[0]);
            
            form.querySelector('[name="name"]').value = '';
        } else {
            alert('Error creating playlist. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while creating the playlist.');
    });
});