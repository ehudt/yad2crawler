from urllib             import urlencode
from urllib2            import urlopen, build_opener, install_opener, quote, Request, ProxyHandler, HTTPCookieProcessor
from cookielib          import Cookie, CookieJar

PROXY = {
    "http":  "localhost:8888",
    "https": "localhost:8888",
}

class Yad2Client(object):

    def __init__(self):        
        proxy = ProxyHandler(PROXY)
        self.cj = CookieJar()
        opener = build_opener(HTTPCookieProcessor(self.cj), proxy)
        install_opener(opener)


    def add_cookie(self, name, value):
        cookie =  Cookie(version=0, name=name, value=value, port=None,
                         port_specified=False, domain='yad2.co.il',
                         domain_specified=False, domain_initial_dot=False,
                         path='/', path_specified=True, secure=False, expires=None,
                         discard=True, comment=None, comment_url=None,
                         rest={'HttpOnly': None}, rfc2109=False)
        
        self.cj.set_cookie(cookie)


    def clear_cookies(self):
        self.cj.clear()


    def get_url(self, url, headers = {}, args = {}):
        headers["Host"] = "m.yad2.co.il"
        headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        headers["User-Agent"] = "Mozilla/5.0 (Linux; Android 4.2.2; Android SDK built for x86 Build/KK) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36"
        headers["Accept-Language"] = "en-US"
                
        url = url + "?" + urlencode(args) if args else url
        req = Request(url, headers = headers)
        response = urlopen(req)

        return response.read()
