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

function isImage(filename) {
    const exts = [".png", ".jpg", ".jpeg", ".gif", ".tiff"];
    for (let e of exts) {
        if (filename.endsWith(e))
            return true;
    }
    return false;
}

function loadUrl(url) {
    $('#gallery').empty();
    $('#dir').empty();
    let basePath = url.pathname;
    let searchParams = new URLSearchParams();
    searchParams.append("host", url.host);
    searchParams.append("port", url.port);
    $.get(url.href, function (data) {
        $("#dir").html(data);
        $("#dir li a").each(function (index) {
            let filename = $(this).text();
            if (filename.endsWith("/")) {
                // this is a directory - change link
                searchParams.set("path", basePath + filename);
                $(this).attr("href", "?"+searchParams.toString());
            } else if (isImage(filename)) {
                let path = url + "/" + filename;
                $(this).parent().hide();
                $('<div class="image">')
                    .data('image', path)
                    .append($('<p>').text(filename))
                    .appendTo('#gallery');
            } else {
                $(this).attr("href", url.href+filename);
            }
        });
        loadVisible();
    });
}

function getUrlParam(urlParams, name, default_value) {
    if (urlParams.has(name))
        return urlParams.get(name);
    return default_value;
}

$(window).scroll(loadVisible);
const urlParams = new URLSearchParams(window.location.search);
let url = new URL("http://dummy/");
url.host = getUrlParam(urlParams, "host", "localhost");
url.port = getUrlParam(urlParams, "port", 8000);
url.pathname = getUrlParam(urlParams, "path", "/");

loadUrl(url);
