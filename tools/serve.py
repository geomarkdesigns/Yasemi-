"""Local preview server that mimics Vercel clean URLs and the 404 page."""
import http.server, os, sys
import pathlib
ROOT=str(pathlib.Path(__file__).resolve().parent.parent / "public")
PORT=int(sys.argv[1]) if len(sys.argv)>1 else 8765
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s,*a,**k): super().__init__(*a,directory=ROOT,**k)
    def log_message(s,*a): pass
    def send_head(s):
        p=s.path.split("?")[0].rstrip("/") or "/"
        f=os.path.join(ROOT,p.lstrip("/"))
        if p!="/" and not os.path.splitext(p)[1] and os.path.exists(f+".html"): s.path=p+".html"
        elif p in ("/el",): s.path="/el/index.html"
        elif not os.path.exists(os.path.join(ROOT,s.path.split("?")[0].lstrip("/"))) and p!="/":
            s.send_response(404); s.send_header("Content-Type","text/html"); s.end_headers(); return open(os.path.join(ROOT,"404.html"),"rb")
        return super().send_head()
print(f"serving {ROOT} on http://127.0.0.1:{PORT}", flush=True)
http.server.ThreadingHTTPServer(("127.0.0.1",PORT),H).serve_forever()
