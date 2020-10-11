from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys
import os
import io
import urllib.parse
import html


class GalleryRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(path, "index_template.html"), "r") as handle:
            self.template = handle.readlines()
        with open(os.path.join(path, "main.css"), "r") as handle:
            css = handle.readlines()
        with open(os.path.join(path, "main.js"), "r") as handle:
            js = handle.readlines()
        self.template = ''.join(self.template)
        self.template = self.template.replace("{JS}", ''.join(js))
        self.template = self.template.replace("{CSS}", ''.join(css))
        super().__init__(*args, directory=directory, **kwargs)

    @staticmethod
    def _is_image(filename):
        for e in [".png", ".jpg", ".jpeg", ".gif", ".tiff"]:
            if filename.endswith(e):
                return True
        return False

    @staticmethod
    def _escape_file(link_name, display_name):
        ln = urllib.parse.quote(link_name, errors='surrogatepass')
        dn = html.escape(display_name, quote=False)
        return ln, dn

    @staticmethod
    def _make_image(link_name, display_name):
        ln, dn = GalleryRequestHandler._escape_file(link_name, display_name)
        return f'<div class="image" data-image="{ln}"><p>{dn}</p></div>'

    @staticmethod
    def _make_file(link_name, display_name):
        ln, dn = GalleryRequestHandler._escape_file(link_name, display_name)
        return f'<li><a href="{ln}">{dn}</a></li>'

    def list_directory(self, path):
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())

        try:
            display_path = urllib.parse.unquote(self.path, errors='surrogatepass')
        except UnicodeDecodeError:
            display_path = urllib.parse.unquote(path)
        display_path = html.escape(display_path, quote=False)
        enc = sys.getfilesystemencoding()
        title = f'Directory listing for {display_path}'

        dir_listing = ["<ul>"]
        gallery_listing = []
        for name in list:
            fullname = os.path.join(path, name)
            display_name = link_name = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                display_name = name + "/"
                link_name = name + "/"
            if os.path.islink(fullname):
                display_name = name + "@"
            if os.path.isfile(fullname) and self._is_image(fullname):
                gallery_listing.append(self._make_image(link_name, display_name))
            else:
                dir_listing.append(self._make_file(link_name, display_name))
        dir_listing.append("</ul>")
        dir_listing = '\n'.join(dir_listing)
        gallery_listing = '\n'.join(gallery_listing)

        final_html = self.template.replace("{TITLE}", title)
        final_html = final_html.replace("{DIRLIST}", dir_listing)
        final_html = final_html.replace("{GALLERY}", gallery_listing)

        encoded = final_html.encode(enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) >= 2 else 2087
    httpd = HTTPServer(('localhost', port), GalleryRequestHandler)
    print(f"server running at http://{httpd.server_address[0]}:{httpd.server_port}/")
    httpd.serve_forever()
