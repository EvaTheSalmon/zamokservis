var traffic = [[[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0, 0]],
              [[0, 0, 0, 0, 0, 0, 1, 4, 6, 4, 3, 3, 3, 3, 3, 4, 4, 6, 7, 4, 2, 1, 0, 0]],
              [[0, 0, 0, 0, 0, 0, 1, 4, 6, 4, 3, 3, 3, 3, 3, 4, 4, 6, 7, 4, 2, 1, 0, 0]],
              [[0, 0, 0, 0, 0, 0, 1, 4, 5, 4, 3, 3, 3, 3, 3, 4, 4, 6, 7, 4, 2, 1, 0, 0]],
              [[0, 0, 0, 0, 0, 0, 1, 4, 5, 4, 3, 3, 3, 3, 3, 4, 4, 6, 7, 4, 2, 1, 0, 0]],
              [[0, 0, 0, 0, 0, 0, 1, 4, 5, 4, 3, 3, 3, 3, 3, 4, 4, 6, 7, 4, 2, 1, 0, 0]],
              [[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 2, 2, 2, 2, 1, 1, 0, 0]]],
    colorTL = ["#00dd00", "#98ff98", "#ccff00", "#fbf82d", "#f7e164", "#f4c023", "#ff9966", "#ff0000", "#ff4d00", "#f36223"],
    currentTime = new Date, bal = document.getElementById('text_bal'), day = currentTime.getDay(),
    hour = currentTime.getHours();
document.addEventListener("DOMContentLoaded", function (a) {
    bal.innerHTML = (traffic[day][0][hour] + 1).toString(), document.getElementsByClassName("light")[0].style.setProperty("background-color", colorTL[traffic[day][0][hour]], "important")
})