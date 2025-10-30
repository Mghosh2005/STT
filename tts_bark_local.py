# tts_bark_local.py - Bark local template
import time, subprocess, sys
from pathlib import Path
from log_latency import append_result
from config import LOCAL_BARK, TEST_TEXT, OUTPUT_DIR
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
PROVIDER = 'bark'
OUT_PATH = Path(OUTPUT_DIR) / ('output_' + PROVIDER + '_local.wav')

def local_test():
    if not LOCAL_BARK:
        append_result(PROVIDER, len(TEST_TEXT), None, None, None, None, 'skipped', 'local disabled')
        print('[bark] local disabled in config')
        return
    try:
        from bark import generate_audio, preload_models
    except Exception as e:
        append_result(PROVIDER, len(TEST_TEXT), None, None, None, None, 'skipped', 'bark not installed')
        print('[bark] bark package not installed - see README')
        return
    try:
        preload_models()
    except:
        pass
    t0 = time.time()
    audio = generate_audio(TEST_TEXT)
    synth_time = time.time() - t0
    try:
        import soundfile as sf
        sf.write(OUT_PATH, audio, 24000)
        append_result(PROVIDER, len(TEST_TEXT), 0.0, synth_time, None, OUT_PATH.stat().st_size/1024, 'success', 'local')
        print('[bark] saved', OUT_PATH, f'(synth {synth_time:.3f}s)')
    except Exception as e:
        append_result(PROVIDER, len(TEST_TEXT), 0.0, None, None, None, 'error', str(e))
        print('[bark] error saving', e)
    try:
        subprocess.run([sys.executable, 'generate_latency_report.py'], check=False)
    except Exception as e:
        print('Failed to run report generator:', e)

if __name__ == '__main__':
    local_test()
