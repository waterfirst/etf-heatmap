# -*- coding: utf-8 -*-
"""
ETF 모멘텀 히트맵 - 로컬 서버 (CORS 안전장치)
실행: python etf_server.py   또는  start.bat 더블클릭
 - 같은 폴더의 index.html 을 http://localhost:8765 로 서빙
 - /proxy?url=... 로 공공데이터포털 / 네이버 시세 API를 서버 측에서 대신 호출(브라우저 CORS 회피)
 - 실행 시 자동으로 브라우저를 엽니다.
"""
import http.server, socketserver, urllib.parse, urllib.request, ssl, os, sys, webbrowser, threading

PORT = 8765
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=DIRECTORY, **k)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/proxy':
            self.handle_proxy(parsed)
            return
        if parsed.path in ('/', ''):
            self.path = '/index.html'
        return super().do_GET()

    def handle_proxy(self, parsed):
        qs = urllib.parse.parse_qs(parsed.query)
        target = qs.get('url', [None])[0]
        allowed = ('https://apis.data.go.kr', 'https://polling.finance.naver.com')
        if not target or not target.startswith(allowed):
            self.send_error(400, 'invalid url')
            return
        try:
            req = urllib.request.Request(target, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30, context=_ctx) as r:
                data = r.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(('proxy error: ' + str(e)).encode('utf-8'))

    def log_message(self, *a):
        pass


def main():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('127.0.0.1', PORT), Handler) as httpd:
        url = f'http://localhost:{PORT}/index.html'
        print(f'ETF 히트맵 서버 실행 중 → {url}')
        print('종료하려면 이 창에서 Ctrl+C 를 누르세요.')
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\n종료합니다.')


if __name__ == '__main__':
    main()
