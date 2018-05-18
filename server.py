import socketserver
import http.server
import savesvgupload
from communicator import Communicator
from drawing import Drawing

# Always use pybars to inject dynamic/user-generated data into html pages, it
# protects users against XSS automatically.
from pybars import Compiler
compiler = Compiler()

# By default browsers assume port 80 for the http protocol, but for that you'll
# have to start this script with administrator rights
PORT = 8090
HOST = "drawbotpi.local"

# Let's read the html files to serve at the start of the server, such that
# they're cached when we actually need them.
f = open('./public/image.html', 'r', encoding='ISO-8859-1')
comp_image_page = compiler.compile(f.read())
f.close()

upload_page = open('./public/index.html', 'r', encoding='ISO-8859-1').read()

f = open('./public/error.html', 'r', encoding='ISO-8859-1')
comp_error_page = compiler.compile(f.read())
f.close()

start_page = open('./public/start.html', 'r', encoding='ISO-8859-1').read()


class Handler(http.server.BaseHTTPRequestHandler):
    # Main router for GET requests
    def do_GET(s):
        p = s.path
        if p == '' or p == '/':
            s.redirect('/index.html')
        elif p.startswith('/index.html'):
            s.serve_upload_page()
        elif p.startswith('/image.html'):
            s.serve_image_page()
        elif p.startswith('/start.html'):
            s.serve_starting_page()
        elif p.startswith('/uploads/'):
            s.serve_upload()
        else:
            s.serve_error_page(404)

    # Secundary router for post requests
    def do_POST(s):
        if s.path == '/image.html':
            name = savesvgupload.save_svg_upload(s)
        if name:
            s.redirect('/image.html?f=' + name)
        else:
            s.serve_error_page(400)

    # These are the standard headers that should be sent with each response. I
    # want to bundle them in a method for consistency. Also it's important that
    # security-related headers are never forgotten. Useful overview:
    # https://www.owasp.org/index.php/OWASP_Secure_Headers_Project#tab=Headers
    def serve_headers(s, status, content_type=False, end=True):
        s.send_response(status)
        s.send_header('Vary', 'Accept-Encoding')
        if content_type:
            s.send_header('Content-Type', content_type)

        # Prevent the browser from interpreting files as something else than
        # declared by the Content-Type
        s.send_header('X-Content-Type-Options', 'nosniff')
        # Prevent leaking the location or internal IPs
        s.send_header('Referrer-Policy', 'no-referrer')

        if content_type == 'text/html':
            # Turn on the client-side XSS protection mechanisms.
            s.send_header('X-XSS-Protection', '1')
            # Don't allow my pages to render within an iframe - protects the
            # users against clickjacking
            s.send_header('X-Frame-Options', 'sameorigin')

        if end:
            s.end_headers()

    def redirect(s, url):
        s.serve_headers(301, end=False)
        s.send_header('Location', url)
        s.end_headers()

    def serve_upload_page(s):
        s.serve_headers(status=200, content_type='text/html')
        s.wfile.write(bytes(upload_page, encoding='ISO-8859-1'))

    def serve_image_page(s):
        imgurl = s.path.replace('/image.html?f=', '')
        result = comp_image_page({'imgurl': imgurl}).encode('utf-8')
        s.serve_headers(status=200, content_type='text/html')
        s.wfile.write(bytes(result))

    def serve_upload(s):
        # Basic protection against unrestricted file access vulnerabilities
        # https://www.owasp.org/index.php/Unrestricted_File_Upload
        if (not s.path.startswith('/uploads/')) or ('..' in s.path) \
           or (not s.path.endswith('.svg')):
            s.serve_error_page(403)
            return

        s.serve_headers(status=200, content_type='image/svg+xml')

        # Catch and return an error page if the requested upload doesn't exist
        try:
            f = open('./' + s.path, 'r')
            s.wfile.write(f.read().encode('utf-8'))
            f.close()
        except IOError:
            s.serve_error_page(404)

    # Todo: we should probably extract these to a different file (and actually
    # handle all kinds of errors)
    def serve_error_page(s, error):
        if error == 404:
            err = 'Kon de gevraagde pagina niet vinden.'
        elif error == 400:
            err = 'Error 400: Er is iets fout met het formaat van de request'
        elif (error == 401) or (error == 403):
            err = 'Deze pagina is niet voor u toegangkelijk'
        elif error > 500:
            err = 'Er is iets fout gelopen met de server.'
        else:
            err = 'Error {0}'.format(error)

        result_page = comp_error_page({'error': err}).encode('utf8')

        s.serve_headers(status=error, content_type='text/html')
        s.wfile.write(bytes(result_page, encoding='ISO-8859-1'))

    def serve_starting_page(s):
        file = s.path.replace('/start.html?f=', '')
        # Basic protection against evil fake file locations
        if ('http://' in file) or ('..' in file) or ('/' in file):
            s.serve_error_page(403)
            return

        file = './uploads/' + file

        # Todo: error handling here - what if the file isn't found?
        d = Drawing(filename=file)
        instructions = d.instructions()

        s.serve_headers(status=200, content_type='text/html')
        s.wfile.write(bytes(start_page, encoding='ISO-8859-1'))

        com = Communicator()
        for i in instructions:
            print("Sending instruction to drawbot: " + i)
            com.sendcommand(i)
        com.close()


httpd = socketserver.TCPServer((HOST, PORT), Handler)
print('Serving at http://{0}:{1}/ - Press Ctrl+C to stop the server.'
      .format(HOST, PORT))
print('There will be a log of the HTTP requests in STDOUT. Always be ' +
      'careful with the stack traces, sensitive information might be ' +
      'included.')
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    httpd.shutdown()
    httpd.server_close()
    print()  # Final newline after last log
