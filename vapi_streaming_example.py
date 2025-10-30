# vapi_streaming_example.py
# Template WebSocket client that connects to a Vapi streaming endpoint (or a proxy that streams audio).
# Replace WS_URL and headers with real values.
import asyncio, websockets, time, os
from pathlib import Path

WS_URL = os.getenv('VAPI_WS_URL', 'wss://stream.vapi.ai/v1/stream')  # example placeholder
AUTH_TOKEN = os.getenv('VAPI_API_KEY', 'REPLACE_WITH_KEY')
OUT_DIR = 'outputs_vapi'
Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
OUT_PATH = Path(OUT_DIR) / 'vapi_stream_output.wav'

async def run():
    headers = [('Authorization', f'Bearer {AUTH_TOKEN}')]
    t0 = time.time()
    async with websockets.connect(WS_URL, extra_headers=headers) as ws:
        # send initial request frame if required by the endpoint
        await ws.send('{"type": "start", "text": "Hello from Vapi streaming test"}')
        first = None
        received = bytearray()
        while True:
            msg = await ws.recv()
            if isinstance(msg, bytes):
                if first is None:
                    first = time.time()
                received.extend(msg)
            else:
                # text control frames
                try:
                    import json
                    j = json.loads(msg)
                    if j.get('event') in ('end','done','finished'):
                        break
                except:
                    pass
            if len(received) > 50_000_000:
                break
        req_latency = (first - t0) if first else None
        if received:
            with open(OUT_PATH, 'wb') as f:
                f.write(received)
            print(f'Saved streaming audio to {OUT_PATH} (first byte latency {req_latency:.3f}s)')
        else:
            print('No audio received')

if __name__ == '__main__':
    asyncio.run(run())
