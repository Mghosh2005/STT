#!/usr/bin/env python3
"""
Local Microphone -> Streaming STT using VOSK and sounddevice.

Usage (example):
    python stt_streaming_vosk.py --vosk-model "C:\path\to\vosk-model-small-en-us-0.15" --chunk-seconds 1.0 --out transcript.txt
Notes:
 - Make sure vosk and sounddevice are installed and model path points to extracted model folder
"""
import argparse
import queue
import sys
import time
from pathlib import Path
import json
import numpy as np

try:
    import sounddevice as sd
except Exception as e:
    print("sounddevice is required. Install with: pip install sounddevice")
    raise e

try:
    from vosk import Model as VoskModel, KaldiRecognizer
    VOSK_AVAILABLE = True
except Exception:
    VOSK_AVAILABLE = False

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SECONDS = 1.0
q = queue.Queue()


def callback(indata, frames, time_info, status):
    if status:
        print("Audio status:", status, file=sys.stderr)
    data = indata.copy() if indata.dtype == np.int16 else (indata * 32767).astype(np.int16)
    q.put(data.tobytes())


class VoskStreamer:
    def _init_(self, model_path: str):
        if not VOSK_AVAILABLE:
            raise RuntimeError("VOSK not installed. pip install vosk")
        if not Path(model_path).exists():
            raise FileNotFoundError(f"VOSK model not found at {model_path}")
        print("Loading VOSK model...")
        self.model = VoskModel(model_path)
        self.rec = KaldiRecognizer(self.model, SAMPLE_RATE)

    def transcribe_chunk(self, pcm_bytes: bytes):
        if self.rec.AcceptWaveform(pcm_bytes):
            return self.rec.Result()
        else:
            return self.rec.PartialResult()


def processing_loop(backend, write_output: Path = None):
    bytes_per_second = SAMPLE_RATE * 2 * CHANNELS
    target_bytes = int(bytes_per_second * CHUNK_SECONDS)
    buffer = bytearray()
    out_fp = open(write_output, "a", encoding="utf-8") if write_output else None
    print("Start speaking... Press Ctrl+C to stop.")
    try:
        while True:
            try:
                buffer.extend(q.get(timeout=1.0))
            except queue.Empty:
                continue
            while len(buffer) >= target_bytes:
                chunk = bytes(buffer[:target_bytes])
                del buffer[:target_bytes]
                res_json = backend.transcribe_chunk(chunk)
                try:
                    text = json.loads(res_json).get("text", "")
                except Exception:
                    text = ""
                print(f"[{time.strftime('%H:%M:%S')}] VOSK -> {text}")
                if out_fp:
                    out_fp.write(f"{time.time()}\tVOSK\t{text}\n")
    except KeyboardInterrupt:
        print("Stopping processing loop...")
    finally:
        if out_fp:
            out_fp.close()


def main():
    global CHUNK_SECONDS
    parser = argparse.ArgumentParser(description="Local streaming STT")
    parser.add_argument("--vosk-model", type=str, required=True,
                        help="Path to VOSK model directory (extracted folder)")
    parser.add_argument("--chunk-seconds", type=float, default=CHUNK_SECONDS,
                        help="Seconds per audio chunk")
    parser.add_argument("--out", type=str, default=None,
                        help="Append transcripts to this file")
    args = parser.parse_args()

    CHUNK_SECONDS = float(args.chunk_seconds)

    backend = VoskStreamer(args.vosk_model)
    blocksize = int(SAMPLE_RATE * CHUNK_SECONDS)
    try:
        with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=blocksize, dtype='int16',
                               channels=CHANNELS, callback=callback):
            processing_loop(backend, write_output=Path(args.out) if args.out else None)
    except Exception as e:
        print("Could not open microphone stream:", e)
        sys.exit(1)


if _name_ == "_main_":
    main()
