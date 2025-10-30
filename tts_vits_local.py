# tts_vits_local.py - VITS local template (requires vits_inference.synthesize)
import time, subprocess, sys
from pathlib import Path
from log_latency import append_result
from config import LOCAL_VITS, TEST_TEXT, OUTPUT_DIR
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
PROVIDER = 'vits'
OUT_PATH = Path(OUTPUT_DIR) / ('output_' + PROVIDER + '_local.wav')

def local_test():
    if not LOCAL_VITS:
        append_result(PROVIDER, len(TEST_TEXT), None, None, None, None, 'skipped', 'local disabled')
        print('[vits] local disabled in config')
        return
    try:
        from vits_inference import synthesize, SAMPLE_RATE
    except Exception as e:
        append_result(PROVIDER, len(TEST_TEXT), None, None, None, None, 'skipped', 'vits_inference missing')
        print('[vits] vits_inference module not found - provide implementation')
        return
    t0 = time.time()
    audio = synthesize(TEST_TEXT)
    synth_time = time.time() - t0
    try:
        import soundfile as sf
        sf.write(OUT_PATH, audio, SAMPLE_RATE)
        append_result(PROVIDER, len(TEST_TEXT), 0.0, synth_time, None, OUT_PATH.stat().st_size/1024, 'success', 'local')
        print('[vits] saved', OUT_PATH, f'(synth {synth_time:.3f}s)')
    except Exception as e:
        append_result(PROVIDER, len(TEST_TEXT), 0.0, None, None, None, 'error', str(e))
        print('[vits] error saving', e)
    try:
        subprocess.run([sys.executable, 'generate_latency_report.py'], check=False)
    except Exception as e:
        print('Failed to run report generator:', e)

if __name__ == '__main__':
    local_test()
