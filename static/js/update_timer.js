// Updating the timer display on the client side

// This function fetches the updated timer content from the server every second
setInterval(function () {
    fetch('/').then(response => response.text()).then(data => {
        // Parse the HTML content received from the server
        const parser = new DOMParser();
        const htmlDocument = parser.parseFromString(data, 'text/html');
        // Extract the timer message from the parsed HTML
        const timerMessage = htmlDocument.getElementById('timer').innerText;
        // Call the updateTimer function to update the timer display
        updateTimer(timerMessage);
    });
}, 1000);

// This function updates the timer display in the browser
function updateTimer(message) {
    document.getElementById("timer").innerText = message;
}
