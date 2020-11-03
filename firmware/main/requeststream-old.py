"""Open an arbitrary URL.
Adapted for Micropython by Alex Cowan <acowan@gmail.com>
Works in a similar way to python-requests http://docs.python-requests.org/en/latest/
"""

import usocket as socket

try:
    import ussl as ssl
except:
    import ssl
import binascii


class URLOpener:
    def __init__(
        self,
        url,
        method,
        params={},
        data={},
        headers={},
        cookies={},
        auth=(),
        timeout=5,
    ):
        self.status_code = 0
        self.headers = {}
        self.text = ""
        self.url = url
        self.buffer = b""
        self.socket = None

        print(self.url)
        [scheme, host, port, path, query_string] = urlparse(self.url)
        print("urlopener", scheme, host, port, path, query_string)
        if auth and isinstance(auth, tuple) and len(auth) == 2:
            headers["Authorization"] = "Basic %s" % (
                b64encode("%s:%s" % (auth[0], auth[1]))
            )
        if scheme == "http":
            addr = socket.getaddrinfo(host, int(port))[0][-1]
            print("urlopener scheme http", addr)
            s = socket.socket()
            s.settimeout(5)
            s.connect(addr)

        else:
            sock = socket.socket()
            sock.settimeout(5)
            s = ssl.wrap_socket(sock)
            print("addr info: ", socket.getaddrinfo(host, int(port))[0][-1])
            s.connect(socket.getaddrinfo(host, port)[0][-1])
        if params:
            enc_params = urlencode(params)
            path = path + "?" + enc_params.strip()
        header_string = "Host: %s\r\n" % host
        if headers:
            for k, v in headers.items():
                header_string += "%s: %s\r\n" % (k, v)
        if cookies:
            for k, v in cookies.items():
                header_string += "Cookie: %s=%s\r\n" % (k, quote_plus(v))
        request = b"%s %s HTTP/1.0\r\n%s" % (method, path, header_string)
        if data:
            if isinstance(data, dict):
                enc_data = urlencode(data)
                if not headers.get("Content-Type"):
                    request += "Content-Type: application/x-www-form-urlencoded\r\n"
                request += "Content-Length: %s\r\n\r\n%s\r\n" % (
                    len(enc_data),
                    enc_data,
                )
            else:
                request += "Content-Length: %s\r\n\r\n%s\r\n" % (len(data), data)
        request += "\r\n"
        print("REQUEST", request)
        s.send(request)
        response = s.recv(4096)
        if response == b"HTTP/1.0 200 OK\r\n":
            self.status_code = 200

            headerBuf = b""

            chunk = s.recv(4096)
            while chunk.find(b"\xe9") == -1:
                headerBuf += chunk

                # loop and discard data until we get a chunk that includes the magic start byte
                # to indicate the start of the firmware image
                chunk = s.recv(4096)
            headerBuf += chunk

            # Parse headers
            headerBuf = headerBuf[: headerBuf.find(b"\xe9")]
            self.headers = self.parseHeaders(headerBuf)
            bytesToDownload = int(headers["Content-Length"])
            expectedBlocks = ceil(bytesToDownload / self.blockSize)

            # discard the contents before the magic start byte
            chunk = chunk[chunk.find(b"\xe9") :]

        self.socket = s
        self._get_headers()

        # while 1:
        #     print("urlopener inside loop")
        #     recv = s.recv(1024)
        #     if len(recv) == 0:
        #         break
        #     self.text += recv.decode()
        # s.close()
        # self._parse_result()

    def close(self):
        self.socket.close()

    def _get_headers(self):
        while self.buffer.find(b"\r\n\r\n") == -1:
            chunk = self.socket.recv(1024)
            if len(chunk) == 0:
                self.socket.close()
                break
            self.buffer += chunk

        key, value = self._extract_header()
        while key is not None:
            self.headers[key] = value
            key, value = self._extract_headers()

    def _parse_headers(self):
        """Parse header string and return dictionary of headers"""
        headerString = self.buffer[0 : self.buffer.find(b"\r\n\r\n")]
        headerStrings = headerString.split(b"\r\n")
        self.headers = {
            row.split(b":")[0]
            .decode("utf-8")
            .strip(): row.split(b":")[1]
            .decode("utf-8")
            .strip()
            for row in headerStrings
            if row.find(b":") != -1
        }

    def read(self):
        return self.text

    def _parse_result(self):
        self.text = self.text.split("\r\n")
        while self.text:
            line = self.text.pop(0).strip()
            if line == "":
                break
            if line[0:4] == "HTTP":
                data = line.split(" ")
                self.status_code = int(data[1])
                continue
            if len(line.split(":")) >= 2:
                data = line.split(":")
                self.headers[data[0]] = (":".join(data[1:])).strip()
                continue
        self.text = "\r\n".join(self.text)
        return


def urlparse(url):
    scheme = url.split("://")[0].lower()
    url = url.split("://")[1]
    host = url.split("/")[0]
    path = "/"
    data = ""
    port = 80
    if scheme == "https":
        port = 443
    if host != url:
        path = "/" + "/".join(url.split("/")[1:])
        if path.count("?"):
            if path.count("?") > 1:
                raise Exception("URL malformed, too many ?")
            [path, data] = path.split("?")
    if host.count(":"):
        [host, port] = host.split(":")
    if path[0] != "/":
        path = "/" + path
    return [scheme, host, port, path, data]


def get(url, params={}, **kwargs):
    return urlopen(url, "GET", params=params, **kwargs)


def post(url, data={}, **kwargs):
    return urlopen(url, "POST", data=data, **kwargs)


def put(url, data={}, **kwargs):
    return urlopen(url, "PUT", data=data, **kwargs)


def delete(url, **kwargs):
    return urlopen(url, "DELETE", **kwargs)


def head(url, **kwargs):
    return urlopen(url, "HEAD", **kwargs)


def options(url, **kwargs):
    return urlopen(url, "OPTIONS", **kwargs)


def urlopen(
    url,
    method="GET",
    params={},
    data={},
    headers={},
    cookies={},
    auth=(),
    timeout=5,
    **kwargs
):
    orig_url = url
    attempts = 0
    print(url, method, params, data, headers, cookies, auth, timeout)
    result = URLOpener(url, method, params, data, headers, cookies, auth, timeout)
    print(result)
    ## Maximum of 4 redirects
    while attempts < 4:
        attempts += 1
        if result.status_code in (301, 302):
            url = result.headers.get("Location", "")
            if not url.count("://"):
                [scheme, host, path, data] = urlparse(orig_url)
                url = "%s://%s%s" % (scheme, host, url)
            if url:
                result = URLOpener(url)
            else:
                raise Exception("URL returned a redirect but one was not found")
        else:
            return result
    return result


always_safe = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "abcdefghijklmnopqrstuvwxyz" "0123456789" "_.-"
)


def quote(s):
    res = []
    replacements = {}
    for c in s:
        if c in always_safe:
            res.append(c)
            continue
        res.append("%%%x" % ord(c))
    return "".join(res)


def quote_plus(s):
    if " " in s:
        s = s.replace(" ", "+")
    return quote(s)


def unquote(s):
    """Kindly rewritten by Damien from Micropython"""
    """No longer uses caching because of memory limitations"""
    res = s.split("%")
    for i in xrange(1, len(res)):
        item = res[i]
        try:
            res[i] = chr(int(item[:2], 16)) + item[2:]
        except ValueError:
            res[i] = "%" + item
    return "".join(res)


def unquote_plus(s):
    """unquote('%7e/abc+def') -> '~/abc def'"""
    s = s.replace("+", " ")
    return unquote(s)


def urlencode(query):
    if isinstance(query, dict):
        query = query.items()
    l = []
    for k, v in query:
        if not isinstance(v, list):
            v = [v]
        for value in v:
            k = quote_plus(str(k))
            v = quote_plus(str(value))
            l.append(k + "=" + v)
    return "&".join(l)


def b64encode(s, altchars=None):
    """Reproduced from micropython base64"""
    if not isinstance(s, (bytes, bytearray)):
        raise TypeError("expected bytes, not %s" % s.__class__.__name__)
    # Strip off the trailing newline
    encoded = binascii.b2a_base64(s)[:-1]
    if altchars is not None:
        if not isinstance(altchars, bytes_types):
            raise TypeError("expected bytes, not %s" % altchars.__class__.__name__)
        assert len(altchars) == 2, repr(altchars)
        return encoded.translate(bytes.maketrans(b"+/", altchars))
    return encoded


if __name__ == "__main__":
    # url = "https://api.github.com/repos/quantumlemur/gardening/contents/api/static/style.css"
    # headers = {
    #     "Authorization": "token fec0ca29254694a0496317d96710a560f178c847",
    #     "Accept": "application/vnd.github.v3.raw",
    # }
    url = "https://google.com"
    headers = {}
    rs = get(url=url, headers=headers)
    print(rs.headers)
    rs.close()