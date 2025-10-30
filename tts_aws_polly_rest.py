# tts_aws_polly_rest.py - AWS Polly via boto3 (uses boto3, which is standard)
import time, os, subprocess, sys
from pathlib import Path
from log_latency import append_result
from config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, TEST_TEXT, OUTPUT_DIR
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
PROVIDER = 'aws_polly'
OUT_PATH = Path(OUTPUT_DIR) / ('output_' + PROVIDER + '_rest.mp3')

def rest_test():
    if not (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_REGION):
        append_result(PROVIDER, len(TEST_TEXT), None, None, None, None, 'skipped', 'no aws creds')
        print('[aws_polly] missing AWS creds')
        return
    import boto3, subprocess, sys
    session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION)
    polly = session.client('polly')
    t0 = time.time()
    resp = polly.synthesize_speech(Text=TEST_TEXT, OutputFormat='mp3', VoiceId='Joanna')
    req_latency = time.time() - t0
    if 'AudioStream' in resp:
        data = resp['AudioStream'].read()
        with open(OUT_PATH, 'wb') as f:
            f.write(data)
        append_result(PROVIDER, len(TEST_TEXT), req_latency, None, None, OUT_PATH.stat().st_size/1024, 'success', 'rest')
        print(f'[aws_polly] saved', OUT_PATH, f'(req {req_latency:.3f}s)')
    else:
        append_result(PROVIDER, len(TEST_TEXT), req_latency, None, None, None, 'error', 'no AudioStream')
        print('[aws_polly] synth failed')
    try:
        subprocess.run([sys.executable, 'generate_latency_report.py'], check=False)
    except Exception as e:
        print('Failed to run report generator:', e)

if __name__ == '__main__':
    rest_test()
