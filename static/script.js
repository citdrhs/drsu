document.getElementById("homePage").addEventListener("click", function () {
    const targetUrl = this.dataset.url;
    window.location.href = targetUrl;
});