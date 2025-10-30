# tts_coqui_local.py - Coqui TTS local template
import time, subprocess, sys
from pathlib import Path
from log_latency import append_result
from config import LOCAL_COQUI, TEST_TEXT, OUTPUT_DIR
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
PROVIDER = 'coqui'
OUT_PATH = Path(OUTPUT_DIR) / ('output_' + PROVIDER + '_local.wav')

def local_test():
    if not LOCAL_COQUI:
        append_result(PROVIDER, len(TEST_TEXT), None, None, None, None, 'skipped', 'local disabled')
        print('[coqui] local disabled in config')
        return
    try:
        from TTS.api import TTS
    except Exception as e:
        append_result(PROVIDER, len(TEST_TEXT), None, None, None, None, 'skipped', 'TTS not installed')
        print('[coqui] TTS package not installed')
        return
    tts = TTS(model_name='tts_models/en/ljspeech/tacotron2-DDC', progress_bar=False, gpu=False)
    t0 = time.time()
    wav = tts.tts(TEST_TEXT)
    synth_time = time.time() - t0
    try:
        import soundfile as sf
        sf.write(OUT_PATH, wav, tts.synthesizer.output_sample_rate)
        append_result(PROVIDER, len(TEST_TEXT), 0.0, synth_time, None, OUT_PATH.stat().st_size/1024, 'success', 'local')
        print('[coqui] saved', OUT_PATH, f'(synth {synth_time:.3f}s)')
    except Exception as e:
        append_result(PROVIDER, len(TEST_TEXT), 0.0, None, None, None, 'error', str(e))
        print('[coqui] error saving', e)
    try:
        subprocess.run([sys.executable, 'generate_latency_report.py'], check=False)
    except Exception as e:
        print('Failed to run report generator:', e)

if __name__ == '__main__':
    local_test()
