function updateClock() {

    const now = new Date();

    const options = {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    };

    const date = now.toLocaleDateString('en-IN', options);

    const time = now.toLocaleTimeString();

    document.getElementById("clock").innerHTML =
        date + "<br>" + time;
}

setInterval(updateClock, 1000);

updateClock();
// Refresh every 5 minutes
setInterval(function () {
    location.reload();
}, 300000);