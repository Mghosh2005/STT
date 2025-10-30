# tts_cartesia_streaming.py - Streaming websocket template for cartesia
import asyncio, time, json, subprocess, sys
from pathlib import Path
from log_latency import append_result
from config import TEST_TEXT, OUTPUT_DIR, TIMEOUT, CHUNK_SIZE
import websockets
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
PROVIDER = "cartesia"
OUT_PATH = Path(OUTPUT_DIR) / ("output_" + PROVIDER + "_stream.wav")

async def streaming_test():
    try:
        t0 = time.time()
        ws_url = "wss://api.cartesia.ai/v1/stream"
        headers = [('Authorization','Bearer REPLACE_ME')]
        async with websockets.connect(ws_url, extra_headers=headers) as ws:
            await ws.send(json.dumps({"text": TEST_TEXT}))
            first = None
            received = bytearray()
            while True:
                msg = await ws.recv()
                if isinstance(msg, bytes):
                    if first is None:
                        first = time.time()
                    received.extend(msg)
                else:
                    try:
                        j = json.loads(msg)
                        if j.get('event') in ('end','done','finished'):
                            break
                    except:
                        pass
                if len(received) > 50_000_000:
                    break
            req_latency = (first - t0) if first else None
            synth_time = (time.time() - (first or t0)) if first else None
            if received:
                with open(OUT_PATH, 'wb') as f:
                    f.write(received)
                append_result(PROVIDER, len(TEST_TEXT), req_latency, synth_time, None, OUT_PATH.stat().st_size/1024, 'success', 'stream')
                print(f"[{PROVIDER}] streaming saved", OUT_PATH, f"(req {req_latency:.3f}s)")
            else:
                append_result(PROVIDER, len(TEST_TEXT), None, None, None, None, 'error', 'no audio')
                print(f"[{PROVIDER}] no audio received")
    except Exception as e:
        append_result(PROVIDER, len(TEST_TEXT), None, None, None, None, 'error', str(e))
        print(f"[{PROVIDER}] streaming exception:", e)
    # generate reports after this test
    try:
        subprocess.run([sys.executable, 'generate_latency_report.py'], check=False)
    except Exception as e:
        print('Failed to run report generator:', e)

def run_streaming():
    asyncio.run(streaming_test())

if __name__ == '__main__':
    run_streaming()
