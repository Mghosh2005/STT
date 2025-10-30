# config.py - fill in your API keys and settings
# Fill keys or leave empty to skip that provider's tests.
ELEVENLABS_API_KEY = ""
DEEPGRAM_API_KEY = ""
CARTESIA_API_KEY = ""
SARVAM_API_KEY = ""
GOOGLE_SERVICE_ACCOUNT_JSON = ""  # path to JSON credentials or leave empty
AWS_REGION = ""
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AZURE_SPEECH_KEY = ""
AZURE_SPEECH_REGION = ""

# Local model flags
LOCAL_COQUI = True
LOCAL_BARK = True
LOCAL_VITS = True

# Shared test text used by all scripts
TEST_TEXT = "Hello, this is a TTS latency test. Please measure request and streaming latencies."

# Output settings
OUTPUT_DIR = "outputs"
CSV_OUTPUT = "tts_results.csv"
CHUNK_SIZE = 4096
TIMEOUT = 30
