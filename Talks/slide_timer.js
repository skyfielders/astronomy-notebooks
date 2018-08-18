function setup_timer(hours, minutes) {
    var endtime = new Date();
    endtime.setHours(hours);
    endtime.setMinutes(minutes);
    endtime.setSeconds(0);
    endtime.setMilliseconds(0);

    var style = [
        'position: absolute;',
        'bottom: 0;',
        'right: 0;',
        'padding: 1em 2em;',
        'background-color: white;',
        'z-index: 100;',
        'font-family: monospace;',
        'font-weight: bold;',
        ''
    ].join('');

    var timer_div = $('<div style="' + style + '">Time</div>');
    $('body').append(timer_div);

    var $slides = $('.cell');

    var current_slide_n = -1;
    var last_slide_change = new Date();

    var update_timer = function() {
        var new_slide_n = $('.cell.selected').index() + 1;
        if (current_slide_n != new_slide_n) {
            last_slide_change = new Date();
            current_slide_n = new_slide_n;
        }
        var now = new Date();
        var left = Math.floor((endtime - now) / 1000);
        var leftm = Math.floor(left / 60);
        var lefts = left % 60;
        readout = ('' + current_slide_n + '/' + $slides.length +
                   ' ' + leftm + 'm' + lefts + 's');
        var til_end = endtime - last_slide_change;
        var slides_left = $slides.length - current_slide_n;
        var time_per_slide = til_end / slides_left;
        var ss = (last_slide_change - now) + time_per_slide;
        readout += (' ' + Math.floor(ss / 1000) + 's');
        timer_div.html(readout);
    };

    setInterval(update_timer, 1000);
}
