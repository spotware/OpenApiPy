document.addEventListener("DOMContentLoaded", function (event) {
    copyrightYear = document.querySelector('#copyright-year');
    copyrightYear.innerText = new Date().getUTCFullYear();
});
