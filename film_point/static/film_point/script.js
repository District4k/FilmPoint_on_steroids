document.querySelector('.spark-button').addEventListener('mousemove', function (e) {
    const button = e.currentTarget;

    // Create multiple sparks when mouse moves over the button
    for (let i = 0; i < 100; i++) {  // You can change the number of sparks here
        const spark = document.createElement('div');
        spark.classList.add('spark');

        // Randomly position each spark around the mouse position
        const offsetX = Math.random() * button.offsetWidth;
        const offsetY = Math.random() * button.offsetHeight;

        // Position sparks based on mouse coordinates
        spark.style.left = `${e.offsetX + offsetX - button.offsetWidth / 2}px`;
        spark.style.top = `${e.offsetY + offsetY - button.offsetHeight / 2}px`;

        button.appendChild(spark);

        // Remove the spark element after animation
        setTimeout(() => {
            spark.remove();
        }, 500);
        ; // Time should match the duration of the animation
    }
});


// Add event listener for form submission
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');

    form.addEventListener('submit', (event) => {
        // Check if the password fields match
        if (password.value !== confirmPassword.value) {
            event.preventDefault(); // Stop the form from submitting
            alert('Passwords do not match. Please try again.');
        }
    });
});


function addToWatchlist(movieId) {
    const button = document.getElementById(`watchlistButton-${movieId}`);
    button.classList.add('pulsing'); // Add the pulsing class to animate the button

    fetch('/add_to_watchlist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({movie_id: movieId})
    })
        .then(response => response.json())
        .then(data => {
            // Handle response
            if (data.success) {
                alert('Movie added to watchlist!');
            } else {
                alert('Failed to add movie.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred.');
        })
        .finally(() => {
            // Remove the pulsing class after the animation is done
            setTimeout(() => button.classList.remove('pulsing'), 500);
        });
}

function addToWatchlist(movieId) {
    const button = document.getElementById(`watchlistButton-${movieId}`);
    const spinner = document.createElement('div');
    spinner.classList.add('spinner'); // Create the spinner div

    // Append the spinner to the button and disable the button
    button.appendChild(spinner);
    button.disabled = true;

    fetch('/add_to_watchlist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({movie_id: movieId})
    })
        .then(response => response.json())
        .then(data => {
            // Handle response
            if (data.success) {
                alert('Movie added to watchlist!');
            } else {
                alert('Failed to add movie.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred.');
        })
        .finally(() => {
            // Remove the spinner and re-enable the button
            button.removeChild(spinner);
            button.disabled = false;
        });
}

