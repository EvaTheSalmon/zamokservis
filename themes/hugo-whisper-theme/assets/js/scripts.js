// as soon as loaded - checking theme
document.documentElement.setAttribute("data-theme", "dark");
if (localStorage.getItem("theme") == "light") {
    document.documentElement.setAttribute("data-theme", "light");
} else if (localStorage.getItem("theme") === null && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    //if dark theme preferred, set document with a `data-theme` attribute
    document.documentElement.setAttribute("data-theme", "dark");
    localStorage.setItem("theme","dark");
}

function change_theme(){
    // Get current color
    if(localStorage.getItem("theme") == "dark"){
        var theme = "dark";
    } else {
        var theme = "light";
    }

    if (theme=="dark") {
        // If current = dark then changing to light
        document.documentElement.removeAttribute("data-theme", "dark");
        var theme = "light";
        localStorage.setItem("theme","light");
    } else {
        // If current = light then changing to dark
        document.documentElement.setAttribute("data-theme", "dark");
        var theme = "dark";
        localStorage.setItem("theme","dark");
    }
}

var body = document.querySelector('body')
var menuTrigger = document.querySelector('#toggle-main-menu-mobile');
var menuContainer = document.querySelector('#main-menu-mobile');

menuTrigger.onclick = function () {
    menuContainer.classList.toggle('open');
    menuTrigger.classList.toggle('is-active')
    body.classList.toggle('lock-scroll')
}

var content = document.querySelector('.content.anchor-link-enabled')
if (content) {
    addHeaderAnchors(content);
}

function addHeaderAnchors(content) {
    var headers = content.querySelectorAll('h1, h2, h3, h4');
    // SVG data from https://iconmonstr.com/link-1-svg/
    var linkSvg = ' <svg xmlns="http://www.w3.org/2000/svg" width="16px" height="16px" viewBox="0 0 24 24"><path d="M0 0h24v24H0z" fill="none"></path><path d="M6.188 8.719c.439-.439.926-.801 1.444-1.087 2.887-1.591 6.589-.745 8.445 2.069l-2.246 2.245c-.644-1.469-2.243-2.305-3.834-1.949-.599.134-1.168.433-1.633.898l-4.304 4.306c-1.307 1.307-1.307 3.433 0 4.74 1.307 1.307 3.433 1.307 4.74 0l1.327-1.327c1.207.479 2.501.67 3.779.575l-2.929 2.929c-2.511 2.511-6.582 2.511-9.093 0s-2.511-6.582 0-9.093l4.304-4.306zm6.836-6.836l-2.929 2.929c1.277-.096 2.572.096 3.779.574l1.326-1.326c1.307-1.307 3.433-1.307 4.74 0 1.307 1.307 1.307 3.433 0 4.74l-4.305 4.305c-1.311 1.311-3.44 1.3-4.74 0-.303-.303-.564-.68-.727-1.051l-2.246 2.245c.236.358.481.667.796.982.812.812 1.846 1.417 3.036 1.704 1.542.371 3.194.166 4.613-.617.518-.286 1.005-.648 1.444-1.087l4.304-4.305c2.512-2.511 2.512-6.582.001-9.093-2.511-2.51-6.581-2.51-9.092 0z"/></svg>';
    var anchorForId = function (id) {
        var anchor = document.createElement('a');
        anchor.classList.add('header-anchor');
        anchor.href = "#" + id;
        anchor.innerHTML = linkSvg;
        return anchor;
    };

    for (var h = 0; h < headers.length; h++) {
        var header = headers[h];

        if (typeof header.id !== "undefined" && header.id !== "") {
            header.appendChild(anchorForId(header.id));
        }
    }
}

document.getElementsByClassName("top_bar")[0].style.opacity = 0;
document.getElementsByClassName("top_bar")[0].style.display = "none";
window.onscroll = function () {
    if (window.scrollY > 60) {
        document.getElementsByClassName("top_bar")[0].style.opacity = 1;
        document.getElementsByClassName("top_bar")[0].style.display = "block";
        document.getElementsByClassName("top_bar")[0].style.pointerEvents = "auto";
    } else {
        document.getElementsByClassName("top_bar")[0].style.opacity = 0;
        document.getElementsByClassName("top_bar")[0].style.display = "none";
        document.getElementsByClassName("top_bar")[0].style.pointerEvents = "none";
    }
};