var toggle = (function () {
    var visible = false,
        ele = document.getElementById('list'),
        btn = document.getElementById('btn');

    function flip () {
        var display = ele.style.display;

        ele.style.display = (display === 'block' ? 'none' : 'block');
        visible = !visible;
    }

    btn.addEventListener('click', flip);

    ele.addEventListener('click', function (e) {
        e.stopPropagation();
    });

    document.addEventListener('click', function (e) {
        if (visible && e.target !== btn) flip();
    });

    ele.style.display = 'none';

    return flip;
}());