function loadVisible() {
    let top = $(document).scrollTop(), bottom = top + $(window).height();
    let gallery = $('#gallery > div');
    for (let i = 0; i < gallery.length; i++) {
        let div = gallery.eq(i);
        let y1 = div.position().top, y2 = y1 + div.height();
        if (y1 > bottom || y2 < top) {
            div.css('background-image', '');
            continue;
        }
        div.css('background-image', 'url(' + div.data('image') + ')');
    }
}

function updateColumns(event) {
    $(".image").css("width", `${Math.floor(100/event.target.value)-1}%`);
    loadVisible();
}

$(window).scroll(loadVisible);
$('#numColumns').change(updateColumns);

loadVisible();
