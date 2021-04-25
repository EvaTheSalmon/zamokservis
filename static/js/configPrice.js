var sum = 0, offer_ids;
document.addEventListener("DOMContentLoaded", function (a) {
    main_func()
}), offer_ids = ["offer_lock_div", "offer_safe_div", "offer_auto_div"];

function hideAll() {
    for (var a in offer_ids) try {
        document.getElementById(offer_ids[a]).hidden = !0, document.getElementById(offer_ids[a]).getElementsByTagName('option')[0].selected = 'selected'
    } catch (a) {
    }
}

function main_func() {
    var a = document.getElementById("offer_main"), b = a.options[a.selectedIndex].id;
    switch (b) {
        case"zero":
            hideAll(), sum = 0, appendData();
            break;
        case"lc":
            hideAll(), document.getElementById(offer_ids[0]).hidden = !1, sum = 0, appendData();
            break;
        case"sf":
            hideAll(), document.getElementById(offer_ids[1]).hidden = !1, sum = 0, appendData();
            break;
        case"au":
            hideAll(), document.getElementById(offer_ids[2]).hidden = !1, sum = 0, appendData();
            break;
        case"in":
            hideAll(), sum = 1500, appendData();
            break
    }
}

function lock_func() {
    var a = document.getElementById("offer_lock"), b = a.options[a.selectedIndex].id;
    switch (b) {
        case"offer_lock_zero":
            sum = 0;
            break;
        case"offer_lock_ru":
            sum = 1500;
            break;
        case"offer_lock_im":
            sum = 2000;
            break
    }
    appendData()
}

function safe_func() {
    var a = document.getElementById("offer_safe"), b = a.options[a.selectedIndex].id;
    switch (b) {
        case"offer_safe_zero":
            sum = 0;
            break;
        case"offer_safe_ru":
            sum = 1500;
            break;
        case"offer_safe_sf":
            sum = 2000;
            break
    }
    appendData()
}

function auto_func() {
    var a = document.getElementById("offer_auto"), b = a.options[a.selectedIndex].id;
    switch (b) {
        case"offer_auto_zero":
            sum = 0;
            break;
        case"offer_auto_li":
            sum = 1500;
            break;
        case"offer_auto_gr":
            sum = 2000;
            break;
        case"offer_auto_mh":
            sum = 1500;
            break
    }
    appendData()
}

function appendData() {
    var a = document.getElementById('sum');
    sum == "[object HTMLSpanElement]" && (sum = "0"), a.innerHTML = sum + " руб."
}

document.getElementsByClassName('mainpr')[0].onchange = function () {
    main_func()
}, document.getElementsByClassName('lockpr')[0].onchange = function () {
    lock_func()
}, document.getElementsByClassName('safepr')[0].onchange = function () {
    safe_func()
}, document.getElementsByClassName('autopr')[0].onchange = function () {
    auto_func()
}