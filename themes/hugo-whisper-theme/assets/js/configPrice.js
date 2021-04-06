let sum = 0;
document.addEventListener("DOMContentLoaded", function(event) {
    main_func();
});

const offer_ids = ["offer_lock_div", "offer_safe_div", "offer_auto_div"];

function hideAll() {
    for (let num in offer_ids) try {
        document.getElementById(offer_ids[num]).hidden = true;
        document.getElementById(offer_ids[num]).getElementsByTagName('option')[0].selected = 'selected'
    } catch (err) {
    }
}

function main_func() {
    const e = document.getElementById("offer_main");

    const selected_offer = e.options[e.selectedIndex].id;

    switch (selected_offer) {

        case "zero":
            hideAll();

            sum = 0;
            appendData();
            break;

        case "lc":
            hideAll();
            document.getElementById(offer_ids[0]).hidden = false;


            sum = 0;
            appendData();
            break;

        case "sf":
            hideAll();
            document.getElementById(offer_ids[1]).hidden = false;


            sum = 0;
            appendData();
            break;

        case "au":
            hideAll();
            document.getElementById(offer_ids[2]).hidden = false;


            sum = 0;
            appendData();
            break;

        case "in":
            hideAll();


            sum = 1500;
            appendData();
            break;
    }

}

//---------------------------------------------------------------------------
function lock_func() {
    const e = document.getElementById("offer_lock");

    const selected_offer = e.options[e.selectedIndex].id;

    switch (selected_offer) {

        case "offer_lock_zero":
            sum = 0;
            break;

        case "offer_lock_ru":
            sum = 2000;
            break;

        case "offer_lock_im":
            sum = 2500;
            break;
    }
    appendData();
}

function safe_func() {
    const e = document.getElementById("offer_safe");

    const selected_offer = e.options[e.selectedIndex].id;

    switch (selected_offer) {

        case "offer_safe_zero":
            sum = 0;
            break;

        case "offer_safe_ru":
            sum = 2000;
            break;

        case "offer_safe_sf":
            sum = 2500;
            break;
    }
    appendData();
}

function auto_func() {
    const e = document.getElementById("offer_auto");

    const selected_offer = e.options[e.selectedIndex].id;

    switch (selected_offer) {

        case "offer_auto_zero":
            sum = 0;
            break;

        case "offer_auto_li":
            sum = 2000;
            break;

        case "offer_auto_gr":
            sum = 2500;
            break;


        case "offer_auto_mh":
            sum = 2000;
            break;
    }
    appendData();
}

function appendData() {
    let sSum = document.getElementById('sum');
    if (sum == "[object HTMLSpanElement]") {
        sum = "0"
    }
    sSum.innerHTML = sum + " руб.";
}


document.getElementsByClassName('mainpr')[0].onchange = function () {
    main_func();
};
document.getElementsByClassName('lockpr')[0].onchange = function () {
    lock_func();
};
document.getElementsByClassName('safepr')[0].onchange = function () {
    safe_func();
};
document.getElementsByClassName('autopr')[0].onchange = function () {
    auto_func();
};