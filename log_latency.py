# log_latency.py - shared logger helper
import csv, time, os
from pathlib import Path

CSV_OUTPUT = os.environ.get('TTS_CSV_OUTPUT', 'tts_results.csv')

def append_result(provider, text_len, req_latency, synth_time, audio_duration, file_size_kb, status, note=""):
    file_exists = Path(CSV_OUTPUT).exists()
    with open(CSV_OUTPUT, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["provider","text_len_chars","request_latency_s","synthesis_time_s","audio_duration_s","file_size_kb","status","note","timestamp"])
        writer.writerow([provider, text_len, "{:.4f}".format(req_latency) if req_latency is not None else "", "{:.4f}".format(synth_time) if synth_time is not None else "", "{:.3f}".format(audio_duration) if audio_duration is not None else "", "{:.1f}".format(file_size_kb) if file_size_kb is not None else "", status, note, time.strftime("%Y-%m-%d %H:%M:%S")])
