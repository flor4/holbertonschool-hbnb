document.addEventListener('DOMContentLoaded', () => {

    // LOGIN FORM
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('http://127.0.0.1:5000/api/v1/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                if (response.ok) {
                    const data = await response.json();
                    document.cookie = `token=${data.access_token}; path=/;`;

                    const loginBtn = document.querySelector('.login-button');
                    if (loginBtn) {
                        loginBtn.textContent = 'Logout';
                        loginBtn.href = '#';
                        loginBtn.onclick = () => {
                            document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
                            window.location.reload();
                        };
                    }

                    window.location.href = 'index.html';
                } else {
                    const errorData = await response.json();
                    errorMessage.textContent = errorData.message || 'Login failed';
                }

            } catch (error) {
                errorMessage.textContent = 'Error connecting to server';
                console.error(error);
            }
        });
    }

    // LOGIN → LOGOUT
    const loginBtn = document.querySelector('.login-button');
    if (loginBtn) {
        const hasToken = document.cookie.split('; ').some(c => c.trim().startsWith('token='));
        if (hasToken) {
            loginBtn.textContent = 'Logout';
            loginBtn.href = '#';
            loginBtn.onclick = () => {
                document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
                window.location.href = 'login.html';
            };
        } else {
            loginBtn.textContent = 'Login';
            loginBtn.href = 'login.html';
        }
    }

    // AUTH + PLACES
    checkAuthentication();

    // COOKIE FUNCTION
    function getCookie(name) {
        return document.cookie
            .split('; ')
            .find(row => row.startsWith(name + '='))
            ?.split('=')[1];
    }

    // CHECK AUTH
    function checkAuthentication() {
        const token = getCookie('token');
        if (!token) return;

        fetchPlaces(token);
        fetchPlaceDetailsIfNeeded(token);
    }

    // FETCH PLACES
    async function fetchPlaces(token) {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/v1/places/', {
                headers: { 'Authorization': 'Bearer ' + token }
            });

            if (response.ok) {
                const places = await response.json();
                displayPlaces(places);
                loadFilter();
            }
        } catch (error) {
            console.error('Error fetching places:', error);
        }
    }

    // DISPLAY PLACES
    function displayPlaces(places) {
        const container = document.getElementById('places-list');
        if (!container) return;

        container.innerHTML = "";

        places.forEach(place => {
            const card = document.createElement('div');
            card.className = "place-card";
            card.dataset.price = place.price;

            card.innerHTML = `
                <img src="https://picsum.photos/400/250?random=${place.id}" alt="${place.title}">
                <h3>${place.title}</h3>
                <p>Price: $${place.price}/night</p>
                <a href="place.html?id=${place.id}" class="details-button">View Details</a>
            `;

            container.appendChild(card);
        });
    }

    // PRICE FILTER
    function loadFilter() {
        const filter = document.getElementById('price-filter');
        if (!filter) return;

        filter.innerHTML = `
            <option value="all">All</option>
            <option value="10">10</option>
            <option value="50">50</option>
            <option value="100">100</option>
        `;

        filter.addEventListener('change', () => {
            const maxPrice = filter.value;
            const places = document.querySelectorAll('.place-card');

            places.forEach(place => {
                const price = Number(place.dataset.price);

                if (maxPrice === "all" || price <= Number(maxPrice)) {
                    place.style.display = "block";
                } else {
                    place.style.display = "none";
                }
            });
        });
    }

    // FETCH PLACE DETAILS
    function fetchPlaceDetailsIfNeeded(token) {
        const placeDetailsContainer = document.getElementById('place-details');
        if (!placeDetailsContainer) return;

        const urlParams = new URLSearchParams(window.location.search);
        const placeId = urlParams.get('id');
        if (!placeId) return;

        fetchPlace(placeId, token);
    }

    async function fetchPlace(placeId, token) {
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/v1/places/${placeId}`, {
                headers: { 'Authorization': 'Bearer ' + token }
            });

            if (response.ok) {
                const place = await response.json();
                displayPlace(place);
            }
        } catch (error) {
            console.error('Error fetching place details:', error);
        }
    }

    // DISPLAY PLACE + ADD REVIEW BUTTON
    function displayPlace(place) {
        const container = document.getElementById('place-details');
        if (!container) return;

        container.innerHTML = `
            <h1>${place.title}</h1>
            <p>Price: $${place.price}/night</p>
            <p>Description: ${place.description || 'No description available'}</p>
            <p>Amenities: ${place.amenities ? place.amenities.map(a => a.name).join(', ') : 'No amenities listed'}</p>
        `;

        // ADD REVIEW BUTTON
        const addReviewSection = document.getElementById('add-review-section');
        if (addReviewSection) {
            addReviewSection.innerHTML = `
                <h2>Add a Review</h2>
                <a href="add_review.html?id=${place.id}" class="details-button">Add a Review</a>
            `;
        }
    }

    // ADD REVIEW
    const reviewForm = document.getElementById('review-form');

    if (reviewForm) {

        const token = getCookie('token');
        if (!token) {
            window.location.href = 'index.html';
        }

        const urlParams = new URLSearchParams(window.location.search);
        const placeId = urlParams.get('id');

        if (!placeId) {
            alert("Invalid place ID.");
            window.location.href = 'index.html';
        }

        reviewForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const reviewText = document.getElementById('review').value.trim();
            const rating = document.getElementById('rating').value;

            if (!reviewText) {
                alert("Review cannot be empty.");
                return;
            }

            try {
                console.log('Submitting review for place:', placeId, 'with token:', token);

                const response = await fetch('http://127.0.0.1:5000/api/v1/reviews/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + token
                    },
                    body: JSON.stringify({
                        place_id: placeId,
                        text: reviewText,
                        rating: Number(rating)
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    alert(data.message || data.error || 'Failed to submit review');
                    return;
                }

                alert('Review submitted successfully!');
                reviewForm.reset();

            } catch (error) {
                console.error('Error submitting review:', error);
                alert('Error submitting review');
            }
        });
    }

});
