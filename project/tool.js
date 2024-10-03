document.getElementById('coordinates-form').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent the form from submitting the traditional way

    // Create a FormData object to capture the input
    const formData = new FormData(this);

    // Send a POST request to Flask backend
    fetch('/generate-map', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const resultContainer = document.getElementById('map-result-container');
        if (data.map_url) {
            // Load the map_result.html content
            fetch(data.map_url)  // This is where we fetch the map_result.html
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(html => {
                resultContainer.innerHTML = html;  // Set the innerHTML to the fetched content
                resultContainer.style.display = 'block';  // Show the result container
                document.getElementById('error-message').textContent = '';  // Clear any error messages
            })
            .catch(error => {
                console.error('Error loading map result:', error);
                document.getElementById('error-message').textContent = 'Error loading map result. Please try again.';
                resultContainer.style.display = 'none';  // Hide the container if there's an error
            });
        } else if (data.error) {
            // Display error message
            document.getElementById('error-message').textContent = data.error;
            resultContainer.style.display = 'none';  // Hide the container if there's an error
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('error-message').textContent = 'An error occurred. Please try again.';
    });
});
