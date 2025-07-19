import ujson
import uasyncio as asyncio
from helpers import *

async def serve_client(reader, writer):
    
    request_line = await reader.readline()
    output("Request:", request_line.decode())

    while await reader.readline() != b"\r\n":
        pass
    

    if 'GET /status_json' in request_line:
        response_body = ujson.dumps(json_data)
        content_type = "application/json"

    elif 'GET /status' in request_line:
        try:
            with open('status.html', 'r') as f:
                response_body = f.read()
            content_type = "text/html"
        except Exception:
            response_body = "<h1>500 Internal Server Error</h1><p>Could not load page.</p>"
            content_type = "text/html"
    

    writer.write('HTTP/1.1 200 OK\r\n')
    writer.write(f'Content-Type: {content_type}\r\n')
    writer.write('Connection: close\r\n\r\n')
    writer.write(response_body)
    await writer.drain()
    await writer.wait_closed()

async def start_server():
    server = await asyncio.start_server(serve_client, "0.0.0.0", 80)
    output("Web server running on port 80")
    while True:
        await asyncio.sleep(1)
