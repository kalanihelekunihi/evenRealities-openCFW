# Even Android App — Audio & ASR Pipeline

> Extracted from `even_android.apk` (com.even.sg), 2026-03-14.

## Architecture Overview

The Even app uses a sophisticated hybrid on-device + cloud audio pipeline:

```
Glasses Mic (LC3) → BLE (NUS) → Phone → Audio Pipeline → ASR → Display
                                   │
                                   ├── On-device: libeven.so (ML enhancement)
                                   ├── On-device: Sherpa-ONNX (offline ASR)
                                   └── Cloud: Azure Speech / Soniox (online ASR)
```

## Audio Layer (flutter_ezw_audio)

### Package Structure
```
flutter_ezw_audio/
  ├── audio_algorithm/
  │   ├── audio_enhance_proxy.dart    ML audio enhancement proxy
  │   ├── dart/even_agc.dart          Automatic Gain Control (Dart)
  │   └── model/
  │       ├── binding.dart            FFI bindings to libeven.so
  │       ├── even_process.dart       Audio processing pipeline
  │       ├── speech.dart             Speech models
  │       └── generated/              Protobuf for native IPC
  │           ├── bert.pb.dart        BERT NLU models
  │           ├── common.pbenum.dart  Status codes
  │           ├── noise_reduction.pb.dart  Noise reduction config
  │           ├── speech.pb.dart      Speech processing config
  │           └── speech_enhance.pb.dart   Speech enhancement config
  ├── audio_manager.dart              Central audio manager
  ├── audio_subcriber_entity.dart     Audio event subscribers
  ├── config/
  │   ├── audio_config.dart           Audio configuration
  │   └── speech_config.dart          Speech processing config
  ├── debug_file_manager.dart         Audio debug recording
  ├── interface/
  │   ├── audio_interface.dart        Audio interface
  │   └── i_algorithm.dart            Algorithm interface
  └── mic_audio.dart                  Microphone input
```

### Native ML Library (libeven.so — 30.5MB)

C++ library with protobuf IPC, exposing:

| Module | Description |
|--------|-------------|
| `speech_enhance_module::SpeechEnhance` | Real-time speech enhancement |
| `bert::interface` | BERT intent recognition (NLU) |
| `speech::interface` | Speech processing pipeline |
| `speech_enhance::interface` | Enhancement with AGC config |
| `ssr_smoother::interface` | SSR smoothing |
| `example::interface` | Example/test interface |

**Protobuf definitions for native IPC:**
- `bert.proto` — BERT model: `BatchInferInput`, `InferOutput`, `LoadModelInput/Output`, `Intent`, `Entity`, `EntityType`
- `speech.proto` — Speech: `SpeechInput`, `SpeechOutput`, `SpeechMetrics`, `AGCConfig`, `SpeechEnhanceConfig`, `SetConfigInput/Output`
- `speech_enhance.proto` — Enhancement: `LoadModelFromFileInput`, `LoadModelFromBufferInput`, `LoadModelOutput`, `ResetOutput`
- `noise_reduction.proto` — Noise reduction config
- `common.proto` — `StatusCode` enum

**Key finding**: The app loads BERT and speech enhancement models from files/buffers at runtime, enabling on-device NLU without cloud dependency.

### LC3 Codec (flutter_ezw_lc3 + liblc3.so — 173KB)
- LC3 (Low Complexity Communication Codec) for BLE audio
- Used for glasses microphone audio over NUS characteristic
- 172KB native library — lightweight real-time codec

## ASR Layer (flutter_ezw_asr)

### Dual-Provider Architecture
The app supports **two ASR providers** running in parallel or selectively:

```
flutter_ezw_asr/
  ├── proto/
  │   ├── transcribe_event.pb.dart        Protobuf for transcribe events
  │   └── transcribe_event.pbenum.dart    TranscribeEventType enum
  ├── src/
  │   ├── common/
  │   │   ├── processor_interface.dart    Base processor
  │   │   ├── soniox_configuration_base.dart  Soniox base config
  │   │   ├── soniox_context.dart         Soniox context
  │   │   ├── soniox_websocket_callback.dart  Soniox WS callbacks
  │   │   └── soniox_websocket_manager.dart   Soniox WS manager
  │   ├── transcribe/
  │   │   ├── configuration/
  │   │   │   ├── azure_transcribe_configuration.dart
  │   │   │   └── soniox_transcribe_configuration.dart
  │   │   ├── recognizer/
  │   │   │   ├── base_transcribe_recognizer.dart
  │   │   │   ├── azure_transcribe_recognizer.dart
  │   │   │   └── soniox_transcribe_recognizer_v2.dart
  │   │   ├── result/
  │   │   │   ├── transcribe_output_result.dart
  │   │   │   ├── azure_transcribe_result.dart
  │   │   │   └── soniox_transcribe_result.dart
  │   │   ├── utils/
  │   │   │   ├── azure_transcribe_processor.dart
  │   │   │   ├── soniox_transcribe_processor.dart
  │   │   │   ├── soniox_quality_statistics.dart
  │   │   │   ├── soniox_segmentation_helper.dart
  │   │   │   ├── soniox_timing_storage.dart
  │   │   │   └── segmentation/
  │   │   │       ├── break_reason.dart
  │   │   │       ├── context_analyzer.dart
  │   │   │       ├── punctuation_analyzer.dart
  │   │   │       └── quote_tracker.dart
  │   │   ├── transcribe_recognizer.dart
  │   │   ├── transcribe_recognizer_factory.dart
  │   │   └── sonix_sentence_break_token.dart
  │   ├── types/
  │   │   ├── enums.dart
  │   │   ├── error.dart
  │   │   └── language.dart
  │   └── utils/
  │       └── simple_vad_processor.dart   Voice Activity Detection
  └── flutter_ezw_asr.dart
```

### Provider 1: Azure Speech Services
- **Native SDK**: `libMicrosoft.CognitiveServices.Speech.core.so` (8.5MB)
- Extensions: audio.sys, codec, kws (keyword spotting), kws.ort (ONNX keyword), lu (language understanding), silk_codec, java.bindings
- `AzureAsrConfig` — Configuration model
- `AzureTranscribeProcessor` — Real-time processing
- `AzureTranscribeRecognizer` — Recognition engine
- `AzureTranscribeResult` — Result model
- `getAzureTranslationConfiguration` — Translation config from server

### Provider 2: Soniox
- WebSocket-based real-time ASR
- `SonioxTranscribeRecognizerV2` — Current recognizer version
- `SonioxTranscribeProcessor` / `SonioxSegmentationHelper` — Processing
- `SonioxQualityStatistics` / `SonioxTimingStorage` — Quality tracking
- `SonioxWebsocketManager` / `SonioxWebsocketCallback` — Connection management
- Sentence break detection with context/punctuation/quote analysis

### Provider 3: Sherpa-ONNX (On-Device)
- **Native Libraries**: `libsherpa-onnx-c-api.so` (4.6MB) + `libonnxruntime.so` (16MB)
- On-device ASR without cloud connectivity
- ONNX Runtime for model inference

### TranscribeEventType (from transcribe_event.proto)
```protobuf
enum TranscribeEventType {
  recognizing = 0;      // Partial recognition
  recognized = 1;       // Final recognition
  synthesizing = 2;     // TTS synthesis
  sessionStarted = 3;
  sessionStopped = 4;
  speechStartDetected = 5;
  speechEndDetected = 6;
  canceled = 7;
  error = 8;
}
```

### TranscribeResult
```protobuf
message TranscribeResult {
  string text = 1;
  string reason = 2;
  bool is_final = 3;
  string session_id = 4;
  int64 id = 5;
}
```

## Translation Layer

### TranslationEventType (from translation_event.proto)
Same enum values as TranscribeEventType, plus:
```protobuf
message TranslationResult {
  string original = 1;     // Source language text
  string target = 2;       // Target language text
  string reason = 3;
  bool is_final = 4;
  string session_id = 5;
  int64 id = 6;
  int64 offset = 7;        // Audio offset (timing)
  int64 duration = 8;      // Audio duration
}
```

## AI Agent State Machine

The `ai_agent` service implements a full state machine:

```
idle → wakeup → asr (listening) → cmd_dispatch → ai (processing) → stay → idle
                   ↑                    |
                   └────────────────────┘  (on new wake word)
```

### States
| State | File | Description |
|-------|------|-------------|
| `IdleState` | idle_state.dart | Waiting for wake word |
| `WakeupState` | wakeup_state.dart | Wake word detected, activating |
| `AsrState` | asr_state.dart | Listening and transcribing |
| `CmdDispatchState` | cmd_dispatch_state.dart | Routing ASR result to handler |
| `AiState` | ai_state.dart | AI processing and display |
| `StayState` | stay_state.dart | Staying active for follow-up |

### Support Components
- `AiAgentConfig` — Agent configuration
- `AiAgentContext` — Conversation context
- `AudioRecorder` / `AudioRingBuffer` — Audio capture
- `VadHelper` — Voice Activity Detection
- `AsrEngineHelper` — ASR engine selection
- `TextStreamManager` — Streaming text to glasses display
- `CancellableFutureManager` — Async task management
- `AiBtCmdManager` — BLE command manager for AI

## Speech Enhancement Config (from libeven.so protobuf)
```
speechEnhanceEnable: (bool)
minSpeechDuration: (int ms)
maxSpeechDuration: (int ms)
```

## BERT NLU — On-Device Intent Recognition

### 29 Intent Classes
The BERT model (`bert_load_model` / `bert_infer` via FFI) classifies voice commands:

| Category | Intents |
|----------|---------|
| Feature activation | CONVERSATE_ON, NAVI_ON, TELEP_ON, TRANSC_ON, TRANSL_ON, DISP_ON, SILENT_ON, DP_OFF |
| Brightness | DISP_BRIGHT_AUTO_OFF/ON, DISP_BRIGHT_DEC/INC/MAX/MIN/SET |
| Display distance | DISP_DIST_DEC/INC/MAX/MIN/SET |
| Display height | DISP_HT_DEC/INC/MAX/MIN/SET |
| Notifications | NOTIFY_CLEAR, NOTIFY_OFF, NOTIFY_ON, NOTIFY_SHOW |

### Entity Extraction
- `FROM_LAN` — Source language for translation
- `TO_LAN` — Target language for translation
- `TRANSP` — Transport mode / destination for navigation

### C++ Classes
- `even::bert_module::Bert` — BERT model with WordPiece tokenizer
- `even::bert_module::IntentModel` — ONNX intent classification
- `even::bert_module::Tokenizer` — WordPiece with INTEGER_TOKEN support

## On-Device LLM (llama.cpp)

libeven.so includes a **full llama.cpp build** supporting **98 model architectures**:
- llama, qwen, qwen2, qwen3, deepseek, deepseek2
- gemma, gemma2, gemma3, phi2, phi3
- command_r, and many more
- GGUF model loading supported

This enables on-device LLM inference for the EvenAI feature without cloud dependency.

## SSR Smoothing

Two dedicated smoothers for streaming ASR result display:
- `even::EvenAISmoother` — Smooths EvenAI streaming text
- `even::TranslateOneWaySmoother` — Smooths translation output
- Parameters: threshold, chunk_size, energy_diff-based alpha calculation

## Silero VAD Models

Two Voice Activity Detection models bundled:
- `silero_vad.onnx` (2.3MB) — v4
- `silero_vad.v5.onnx` (2.3MB) — v5
- `modeleqlayer4_388_9.onnx` (1.9MB) — Audio EQ model

## Key Insights

1. **Three ASR tiers**: Azure (cloud, highest quality) → Soniox (cloud, WebSocket) → Sherpa-ONNX (offline)
2. **On-device NLU**: BERT model in libeven.so for 29-intent classification without cloud
3. **On-device LLM**: llama.cpp with 98 model architectures for offline EvenAI
4. **Audio quality pipeline**: Noise reduction → Speech enhancement → AGC → ASR
5. **LC3 codec confirmed**: Native library for BLE audio, matching G2 firmware GX8002B codec chip
6. **Dual VAD**: Simple Dart VAD + Silero ONNX VAD (v4+v5) for robust speech detection
7. **SSR smoothing**: Dedicated text smoothers for EvenAI and Translate streaming display
8. **Soniox v2**: Second version of the Soniox recognizer, suggesting active iteration
9. **Debug recording**: `debug_file_manager.dart` suggests ability to dump raw audio
