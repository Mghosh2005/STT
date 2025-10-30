Vapi Integration & Example Code Package
======================================

Files included:
- vapi_integration_analysis.pdf  : The PDF analysis you can read.
- vapi_call_tts_via_vapi.py     : Example Python script showing how to call a custom TTS endpoint through Vapi's REST API.
- vapi_streaming_example.py     : Example WebSocket streaming client template for receiving streamed audio via Vapi or proxy.
- vapi_benchmark_via_vapi.py    : Simple benchmarking script that measures latency when invoking a TTS via Vapi (single-run).
- README.md                      : This file.

How to use:
1) Fill in VAPI_API_KEY and endpoints in the Python files.
2) Install dependencies: pip install requests websockets soundfile
3) Run the scripts to test E2E latency through Vapi.

Note: These are templates; replace placeholders with real Vapi endpoints and provider-specific details.
