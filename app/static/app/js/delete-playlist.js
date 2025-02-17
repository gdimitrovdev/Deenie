function addDeleteListener(button) {
    button.addEventListener('click', function(e) {
        e.preventDefault();
        const url = button.href;
    
        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('Network response error');
            return response.json();
        })
        .then(data => {
            if (data.id) {
                document.getElementById(`playlist-row-${data.id}`).remove()
            } else {
                alert('Error deleting playlist. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the playlist.');
        });
    });
}

let buttons = document.getElementsByClassName('delete-playlist-button');
for (let button of buttons) {
    addDeleteListener(button);
}
