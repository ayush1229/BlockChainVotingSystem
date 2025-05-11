document.getElementById('voterButton').addEventListener('click', function() {
    window.location.href = 'voter.html';
});

document.getElementById('adminButton').addEventListener('click', function() {
    window.location.href = 'admin.html';
});



document.querySelector('a[href="view-results.html"]').addEventListener('click', function() {
    window.location.href = 'view-results.html';
});

document.querySelector('a[href="release-results.html"]').addEventListener('click', function() {
    window.location.href = 'release-results.html';
});

document.querySelector('a[href="create-voting-session.html"]').addEventListener('click', function() {
    window.location.href = 'create-voting-session.html';
});
