import sounddevice as sd
import numpy as np
import torch
import whisper
import queue
import threading
import sys
import time
import os

# ---------------- CONFIG ---------------- #
SAMPLE_RATE = 16000
CHUNK_DURATION = 2.0        # seconds per chunk
OVERLAP_DURATION = 0.5      # overlap between chunks
MODEL_NAME = "small"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ---------------- LOAD MODEL ---------------- #
print(f"🎧 Loading Whisper model '{MODEL_NAME}' on {DEVICE}...")
model = whisper.load_model(MODEL_NAME).to(DEVICE)
print("✅ Model loaded.\n")

# ---------------- GLOBALS ---------------- #
audio_q = queue.Queue()
stop_flag = threading.Event()

# ---------------- RECORD AUDIO ---------------- #
def record_audio():
    """Continuously record microphone input into a queue."""
    def callback(indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)
        audio_q.put(indata.copy())

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32', callback=callback):
        while not stop_flag.is_set():
            time.sleep(0.1)

# ---------------- TRANSCRIBE AUDIO ---------------- #
def transcriber():
    """Continuously process audio chunks from the queue and transcribe them."""
    chunk_size = int(SAMPLE_RATE * CHUNK_DURATION)
    overlap_size = int(SAMPLE_RATE * OVERLAP_DURATION)

    buffer = np.zeros(0, dtype=np.float32)

    print("🎙 Live transcription started... Speak now!\n")

    while not stop_flag.is_set():
        try:
            # Get next audio chunk
            chunk = audio_q.get(timeout=1)
            buffer = np.concatenate((buffer, chunk.flatten()))

            # If enough audio is collected, process it
            if len(buffer) >= chunk_size:
                # Keep overlap for smoother transitions
                segment = buffer[-(chunk_size + overlap_size):]

                # Run Whisper in a background thread
                threading.Thread(target=decode_and_show_subtitles, args=(segment.copy(),), daemon=True).start()

                # Drop the oldest non-overlap part
                buffer = buffer[-overlap_size:]
        except queue.Empty:
            continue

# ---------------- DECODE & DISPLAY ---------------- #
def decode_and_show_subtitles(audio_data):
    """Run Whisper transcription and print subtitles."""
    try:
        # Skip near-silent chunks
        rms = np.sqrt(np.mean(audio_data ** 2))
        if rms < 0.005:
            return

        result = model.transcribe(audio_data, fp16=torch.cuda.is_available(), language="en", verbose=False)
        text = result.get("text", "").strip()

        if text:
            sys.stdout.write(f"\r💬 {text[:100]} ...\n")
            sys.stdout.flush()
    except Exception as e:
        print(f"\n⚠ Decode error: {e}")

# ---------------- MAIN ---------------- #
def main():
    rec_thread = threading.Thread(target=record_audio, daemon=True)
    rec_thread.start()

    try:
        transcriber()
    except KeyboardInterrupt:
        stop_flag.set()
        print("\n🛑 Exiting cleanly...")
    except Exception as e:
        print("❌ Error:", e)
        print("Tip: pip install openai-whisper sounddevice numpy torch")

if name == "main":
    main()
