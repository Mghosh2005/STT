# tts_elevenlabs_rest.py - REST test template for elevenlabs
import time, requests, os, subprocess, sys
from pathlib import Path
from log_latency import append_result
from config import TEST_TEXT, OUTPUT_DIR, TIMEOUT
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

PROVIDER = "elevenlabs"
OUT_PATH = Path(OUTPUT_DIR) / ("output_" + PROVIDER + "_rest.wav")

def rest_test():
    try:
        t0 = time.time()
        url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {'xi-api-key': 'REPLACE_ME'}
        payload = {"text": TEST_TEXT}
        r = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
        req_latency = time.time() - t0
        if r.status_code != 200:
            append_result(PROVIDER, len(TEST_TEXT), req_latency, None, None, None, "error", "status " + str(r.status_code))
            print(f"[{PROVIDER}] REST error", r.status_code, r.text[:200])
        else:
            audio_bytes = r.content
            if audio_bytes:
                with open(OUT_PATH, 'wb') as f:
                    f.write(audio_bytes)
                append_result(PROVIDER, len(TEST_TEXT), req_latency, None, None, OUT_PATH.stat().st_size/1024, 'success', 'rest')
                print(f"[{PROVIDER}] saved", OUT_PATH, f"(req {req_latency:.3f}s)")
            else:
                append_result(PROVIDER, len(TEST_TEXT), req_latency, None, None, None, 'error', 'empty response')
                print(f"[{PROVIDER}] empty response")
    except Exception as e:
        append_result(PROVIDER, len(TEST_TEXT), None, None, None, None, 'error', str(e))
        print(f"[{PROVIDER}] exception:", e)
    # generate reports after this test
    try:
        subprocess.run([sys.executable, 'generate_latency_report.py'], check=False)
    except Exception as e:
        print('Failed to run report generator:', e)

if __name__ == '__main__':
    rest_test()
