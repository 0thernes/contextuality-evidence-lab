"""Serve the local lab with explicit module MIME types, including on Windows."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=8837)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1] / 'docs'
SimpleHTTPRequestHandler.extensions_map.update({'.mjs': 'text/javascript', '.js': 'text/javascript', '.wasm': 'application/wasm'})
server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(SimpleHTTPRequestHandler, directory=str(root)))
print('Contextuality Evidence Lab: http://127.0.0.1:' + str(args.port), flush=True)
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()
