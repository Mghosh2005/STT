# vapi_benchmark_via_vapi.py
# Single-run benchmark script that calls Vapi TTS endpoint and logs latency to console + CSV.
import time, requests, csv, os
from pathlib import Path

VAPI_API_KEY = os.getenv('VAPI_API_KEY', 'REPLACE_WITH_KEY')
VAPI_TTS_ENDPOINT = os.getenv('VAPI_TTS_ENDPOINT', 'https://api.vapi.ai/v1/tts')  # change as needed
OUT_DIR = 'outputs_vapi'
Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
CSV_OUT = 'vapi_benchmark_results.csv'

TEST_TEXT = 'Benchmarking Vapi TTS end-to-end latency.'

def run_once(text):
    headers = {'Authorization': f'Bearer {VAPI_API_KEY}', 'Content-Type': 'application/json'}
    payload = {'text': text}
    t0 = time.time()
    r = requests.post(VAPI_TTS_ENDPOINT, headers=headers, json=payload, timeout=60)
    req_latency = time.time() - t0
    size_kb = None
    out_path = None
    status = 'error'
    if r.status_code == 200:
        out_path = Path(OUT_DIR) / 'vapi_benchmark_out.wav'
        with open(out_path, 'wb') as f:
            f.write(r.content)
        size_kb = out_path.stat().st_size/1024
        status = 'success'
    else:
        print('Error from Vapi:', r.status_code, r.text[:300])
    # append to csv
    with open(CSV_OUT, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if os.path.getsize(CSV_OUT) == 0:
            writer.writerow(['provider','text_len_chars','request_latency_s','file_size_kb','status','timestamp'])
        writer.writerow(['vapi', len(text), f'{req_latency:.4f}', f'{size_kb if size_kb else ""}', status, time.strftime('%Y-%m-%d %H:%M:%S')])
    print('Run:', status, 'latency', req_latency, 's', 'size_kb', size_kb)
    return req_latency, size_kb, out_path

if __name__ == '__main__':
    run_once(TEST_TEXT)
