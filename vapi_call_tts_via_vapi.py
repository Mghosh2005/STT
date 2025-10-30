# vapi_call_tts_via_vapi.py
# Template showing how to invoke a custom TTS through Vapi's REST orchestration endpoint.
# Replace VAPI_API_KEY and VAPI_TTS_ENDPOINT with your actual values.

import time, requests, json, os
from pathlib import Path

VAPI_API_KEY = os.getenv('VAPI_API_KEY', 'REPLACE_WITH_YOUR_KEY')
VAPI_TTS_ENDPOINT = os.getenv('VAPI_TTS_ENDPOINT', 'https://api.vapi.ai/v1/tts')  # example
OUTPUT_DIR = 'outputs_vapi'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

TEST_TEXT = 'Hello from Vapi integration test. This measures end-to-end latency.'

def call_vapi_tts(text):
    headers = {
        'Authorization': f'Bearer {VAPI_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'text': text,
        # 'voice': 'alloy',  # provider-specific parameters may be nested
        # 'tts_provider': 'elevenlabs' # optional depending on Vapi configuration
    }
    t0 = time.time()
    resp = requests.post(VAPI_TTS_ENDPOINT, headers=headers, json=payload, timeout=30)
    req_latency = time.time() - t0
    if resp.status_code != 200:
        print('Vapi TTS call failed:', resp.status_code, resp.text[:400])
        return None, req_latency, resp
    audio_bytes = resp.content
    out_path = Path(OUTPUT_DIR) / 'vapi_tts_output.wav'
    with open(out_path, 'wb') as f:
        f.write(audio_bytes)
    print(f'Saved audio to {out_path} (req latency {req_latency:.3f}s, size {out_path.stat().st_size/1024:.1f} KB)')
    return out_path, req_latency, resp

if __name__ == '__main__':
    call_vapi_tts(TEST_TEXT)
