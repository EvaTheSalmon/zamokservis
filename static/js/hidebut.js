function colapse() {
    var a = document.getElementById("divhide");
    a.style.display === "none" ? (a.style.display = "block", document.getElementById('buttonHide').innerHTML = "Скрыть") : (a.style.display = "none", document.getElementById('buttonHide').innerHTML = "Показать")
}