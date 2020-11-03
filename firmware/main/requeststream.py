import usocket
import ussl


class URLOpener:
    def __init__(
        self,
        url,
        method,
        params={},
        headers={},
        timeout=5,
    ):
        self.status_code = 0
        self.headers = {}
        self.text = ""
        self.url = url
        self.buffer = b""
        self.socket = None


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


def main(use_stream=True):

    s = usocket.socket()

    ai = usocket.getaddrinfo("google.com", 443)
    print("Address infos:", ai)
    addr = ai[0][-1]

    print("Connect address:", addr)
    s.connect(addr)

    s = ussl.wrap_socket(s)
    print(s)

    if use_stream:
        # Both CPython and MicroPython SSLSocket objects support read() and
        # write() methods.
        s.write(b"GET / HTTP/1.0\r\n\r\n")
        print(s.read(4096))
    else:
        # MicroPython SSLSocket objects implement only stream interface, not
        # socket interface
        s.send(b"GET / HTTP/1.0\r\n\r\n")
        print(s.recv(4096))

    s.close()


def urlopen(url, method="GET", params={}, headers={}, timeout=5, **kwargs):
    orig_url = url
    attempts = 0
    print(url, method, params, headers, timeout)
    result = URLOpener(url, method, params, headers, timeout)
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


def get(url, params={}, **kwargs):
    return urlopen(url, "GET", params=params, **kwargs)


if __name__ == "__main__":
    main()