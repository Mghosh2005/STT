# tts_azure_rest.py - Azure Speech SDK example (uses azure-cognitiveservices-speech SDK)
import time, os, subprocess, sys
from pathlib import Path
from log_latency import append_result
from config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION, TEST_TEXT, OUTPUT_DIR
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
PROVIDER = 'azure'
OUT_PATH = Path(OUTPUT_DIR) / ('output_' + PROVIDER + '_rest.wav')

def rest_test():
    try:
        import azure.cognitiveservices.speech as speechsdk
    except Exception as e:
        append_result(PROVIDER, len(TEST_TEXT), None, None, None, None, 'skipped', 'azure sdk not installed')
        print('[azure] azure sdk not installed')
        return
    if not (AZURE_SPEECH_KEY and AZURE_SPEECH_REGION):
        append_result(PROVIDER, len(TEST_TEXT), None, None, None, None, 'skipped', 'no azure creds')
        print('[azure] missing azure creds')
        return
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
    audio_config = speechsdk.audio.AudioOutputConfig(filename=str(OUT_PATH))
    speech_config.speech_synthesis_voice_name = 'en-US-JennyNeural'
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    t0 = time.time()
    result = synthesizer.speak_text_async(TEST_TEXT).get()
    req_latency = time.time() - t0
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        append_result(PROVIDER, len(TEST_TEXT), req_latency, None, None, OUT_PATH.stat().st_size/1024, 'success', 'rest')
        print(f'[azure] saved', OUT_PATH, f'(req {req_latency:.3f}s)')
    else:
        append_result(PROVIDER, len(TEST_TEXT), req_latency, None, None, None, 'error', str(result.reason))
        print('[azure] synth failed', result.reason)
    try:
        subprocess.run([sys.executable, 'generate_latency_report.py'], check=False)
    except Exception as e:
        print('Failed to run report generator:', e)

if __name__ == '__main__':
    rest_test()
