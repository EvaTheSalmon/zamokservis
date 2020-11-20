function colapse() {
    var x = document.getElementById("divhide");
    if (x.style.display === "none") {
        x.style.display = "block";
        document.getElementById('buttonHide').innerHTML  = "Скрыть";
    } else {
        x.style.display = "none";
        document.getElementById('buttonHide').innerHTML = "Показать";
    }
} 