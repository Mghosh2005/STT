# tts_google_rest.py - Google Cloud Text-to-Speech (client library recommended)
import time, os, subprocess, sys
from pathlib import Path
from log_latency import append_result
from config import GOOGLE_SERVICE_ACCOUNT_JSON, TEST_TEXT, OUTPUT_DIR
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
PROVIDER = 'google'
OUT_PATH = Path(OUTPUT_DIR) / ('output_' + PROVIDER + '_rest.mp3')

def rest_test():
    try:
        from google.cloud import texttospeech
    except Exception as e:
        append_result(PROVIDER, len(TEST_TEXT), None, None, None, None, 'skipped', 'google client not installed')
        print('[google] google-cloud-texttospeech not installed')
        return
    if GOOGLE_SERVICE_ACCOUNT_JSON:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_SERVICE_ACCOUNT_JSON
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=TEST_TEXT)
    voice = texttospeech.VoiceSelectionParams(language_code='en-US', ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    t0 = time.time()
    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    req_latency = time.time() - t0
    with open(OUT_PATH, 'wb') as f:
        f.write(response.audio_content)
    append_result(PROVIDER, len(TEST_TEXT), req_latency, None, None, OUT_PATH.stat().st_size/1024, 'success', 'rest')
    print(f'[google] saved', OUT_PATH, f'(req {req_latency:.3f}s)')
    try:
        subprocess.run([sys.executable, 'generate_latency_report.py'], check=False)
    except Exception as e:
        print('Failed to run report generator:', e)

if __name__ == '__main__':
    rest_test()
