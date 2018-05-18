import hashlib
import random
import time

# Might want to change this if the drawing area is really huge, generally this
# is big enough though.
MAX_FILE_SIZE = 10000

# We might want to be cautious when modifying this function, file uploads
# are hard to get right.
def save_svg_upload(s):
    # Has a file actually been submitted?
    # https://www.owasp.org/index.php/Testing_for_HTTP_Parameter_pollution_(OTG-INPVAL-004)
    if ('content-length' not in s.headers) or ('content-type' not in
       s.headers):
        s.serve_error_page(400)
        return False

    boundary = s.headers['Content-Type'].split('=')[1].encode('utf-8')
    content_length = int(s.headers['content-length'])

    remaining = content_length
    file = b''
    line = b''
    while boundary not in line:
        line = s.rfile.readline()
        remaining -= len(line)

    # Let's keep the file size under the realistic size of an svg file. Not
    # restricting this could result in a continuous data stream with the
    # client, taking down the server. Also big files could fill up the
    # limited memory.
    # https://www.owasp.org/index.php/Unrestricted_File_Upload
    #
    # Let's check for a negative or too small file size too to prevent
    # arbitrary memory access (or simply invalid XML files)
    # https://www.owasp.org/index.php/Testing_for_HTTP_Parameter_pollution_(OTG-INPVAL-004)
    if (remaining > MAX_FILE_SIZE) or (remaining <= 200):
        s.serve_error_page(400)
        return False

    while remaining > 0:
        line = s.rfile.readline()
        remaining -= len(line)
        line = line.replace(b'\r', b'')

        if (line == b'\n') or (b'Content-Type' in line) or \
           (b'Content-Disposition' in line):
            continue

        if boundary in line:
            remaining = 0
        else:
            file += line

    # We don't want sensitive data (such as the original filename or
    # uploader's personal info) stored on the server. True random numbers
    # don't exist (https://en.wikipedia.org/wiki/Random_number_generation)
    # so we go for a hash of a random number and the current date.
    hash = hashlib.md5(str(random.random() * time.clock()).encode('utf-8'))
    filename = hash.hexdigest() + '.svg'
    filelocation = './uploads/' + filename

    f = open(filelocation, 'w+')
    f.write(file.decode('utf-8'))
    f.close()

    return filename
