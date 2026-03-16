# Even Android App — Native Libraries

> Extracted from `even_android_arm64.apk` lib/arm64-v8a/, 2026-03-14.

## Library Inventory

| Library | Size | Category | Description |
|---------|------|----------|-------------|
| **libeven.so** | 30.5MB | Even proprietary | On-device ML: speech enhance, BERT NLU, noise reduction |
| **libapp.so** | 29.4MB | Flutter | Compiled Dart AOT snapshot (all business logic) |
| **libnavigator-android.so** | 27.6MB | Mapbox | Turn-by-turn navigation engine |
| **libonnxruntime.so** | 16.0MB | ML | ONNX Runtime inference engine |
| **libmapbox-maps.so** | 12.2MB | Mapbox | Maps rendering SDK |
| **libflutter.so** | 11.3MB | Flutter | Flutter engine runtime |
| **libMicrosoft.CognitiveServices.Speech.core.so** | 8.5MB | Microsoft | Azure Speech Services core |
| **libmapbox-common.so** | 6.3MB | Mapbox | Mapbox shared utilities |
| **libmodpdfium.so** | 4.8MB | PDF | PDFium rendering (Chrome's PDF engine) |
| **libsherpa-onnx-c-api.so** | 4.6MB | ML | Sherpa-ONNX on-device ASR |
| **libMicrosoft.CognitiveServices.Speech.extension.kws.ort.so** | 1.9MB | Microsoft | Keyword spotting with ONNX Runtime |
| **libsqlite3.so** | 1.5MB | Database | SQLite database engine |
| **libc++_shared.so** | 1.3MB | Runtime | C++ standard library |
| **libmodft2.so** | 753KB | Graphics | FreeType font rendering |
| **libmmkv.so** | 718KB | Storage | Tencent MMKV key-value store |
| **libMicrosoft.CognitiveServices.Speech.extension.lu.so** | 516KB | Microsoft | Language Understanding |
| **libsherpa-onnx-cxx-api.so** | 408KB | ML | Sherpa-ONNX C++ API |
| **libMicrosoft.CognitiveServices.Speech.extension.kws.so** | 286KB | Microsoft | Keyword spotting base |
| **libmodpng.so** | 249KB | Graphics | PNG image processing |
| **libMicrosoft.CognitiveServices.Speech.java.bindings.so** | 250KB | Microsoft | Java JNI bindings |
| **libMicrosoft.CognitiveServices.Speech.extension.silk_codec.so** | 180KB | Microsoft | SILK audio codec |
| **liblc3.so** | 173KB | Audio | LC3 BLE audio codec |
| **libMicrosoft.CognitiveServices.Speech.extension.audio.sys.so** | 158KB | Microsoft | System audio routing |
| **libMicrosoft.CognitiveServices.Speech.extension.codec.so** | 137KB | Microsoft | Audio codec extensions |
| **libjniPdfium.so** | 29KB | PDF | PDFium JNI bridge |
| **libdatastore_shared_counter.so** | 7KB | Android | AndroidX DataStore |
| **libmmap_wrapper.so** | 5KB | Storage | Memory-mapped file wrapper |

**Total native code: ~170MB** (before compression)

## 360 Jiagu Packer (assets/)

| Library | Size | Description |
|---------|------|-------------|
| libjiagu_a64.so | 902KB | ARM64 packer/unpacker |
| libjiagu_x64.so | 902KB | x86_64 packer |
| libjiagu_x86.so | 808KB | x86 packer |
| libjiagu.so | 712KB | ARM32 packer |

Loaded by `StubApp.attachBaseContext()` → decrypts `classes.dex` at runtime.

## libeven.so — Deep Analysis

### Purpose
Even's proprietary on-device ML inference library. NOT BLE protocol code.

### C++ Namespaces (from symbol table)
```
even::speech_enhance_module::SpeechEnhance
bert::interface
speech::interface
speech_enhance::interface
ssr_smoother::interface
example::interface
```

### Protobuf Schemas (compiled into binary)
```
descriptor_table_bert_2eproto
descriptor_table_common_2eproto
descriptor_table_example_2eproto
descriptor_table_speech_2eproto
descriptor_table_speech_5fenhance_2eproto
descriptor_table_ssr_5fsmoother_2eproto
```

### FlatBuffers Tables
```
bert::interface::Intent, Entity, BatchInferInput, InferOutput
bert::interface::LoadModelInput, LoadModelOutput
speech::interface::SpeechInput, SpeechOutput, SpeechMetrics
speech::interface::AGCConfig, SpeechEnhanceConfig, SetConfigInput/Output
speech_enhance::interface::LoadModelFromFileInput, LoadModelFromBufferInput
speech_enhance::interface::LoadModelOutput, ResetOutput
ssr_smoother::interface::SetParaInput
```

### Exported Functions
- `speechProcessorProcessExport` — Main speech processing entry point
- `get_available_output_samples` — Buffer management

### Dependencies
- ONNX Runtime references (neural network inference)
- NumPy-style matrix operations
- CUDA/cuBLAS references (compiled with GPU support but runs on CPU)
- llama.cpp references (LLM inference — `libsherpa-onnx` integration)

## libapp.so — Dart AOT Snapshot

### Contents
- Compiled Dart code from all Flutter packages
- 59,122 extractable strings (with min length 8)
- Contains: class names, function names, string constants, file paths
- Dart snapshot sections: `_kDartVmSnapshotInstructions`, `_kDartIsolateSnapshotData`, etc.

### Key Even Packages (by file count)
| Package | Files | Purpose |
|---------|-------|---------|
| even | 869 | Main app |
| even_connect | 119 | BLE protocol |
| dashboard | 68 | Dashboard widgets |
| even_core | 43 | Core services |
| conversate | 40 | Conversation AI |
| teleprompt | 33 | Teleprompter |
| flutter_ezw_asr | 31 | ASR engine |
| even_navigate | 30 | Navigation |
| flutter_ezw_ble | 27 | BLE driver |
| translate | 24 | Translation |

## Microsoft Cognitive Services Speech

### Component Breakdown
| Extension | Purpose |
|-----------|---------|
| core | Main speech recognition and synthesis |
| audio.sys | System audio input/output |
| codec | Audio codec support |
| kws | Keyword spotting (wake word detection) |
| kws.ort | Keyword spotting with ONNX Runtime |
| lu | Language Understanding (LUIS/CLU) |
| silk_codec | SILK audio codec (Skype heritage) |
| java.bindings | JNI bridge to Java/Kotlin |

### InternalContentProvider
```xml
<provider android:name="com.microsoft.cognitiveservices.speech.util.InternalContentProvider"/>
```
Microsoft Speech SDK uses a ContentProvider for internal state management.

## Mapbox Stack

### Components
- `libmapbox-maps.so` (12.2MB) — Map rendering, tiles, styling
- `libmapbox-common.so` (6.3MB) — Shared utilities, networking, caching
- `libnavigator-android.so` (27.6MB) — Turn-by-turn navigation, routing, voice guidance

### SDK Initializers (from AndroidManifest)
```
com.mapbox.navigation.core.internal.MapboxNavigationSDKInitializer
com.mapbox.navigator.MapboxNavigationNativeInitializer
com.mapbox.maps.loader.MapboxMapsInitializer
com.mapbox.common.MapboxSDKCommonInitializer
```

## Sherpa-ONNX (On-Device ASR)

### Components
- `libsherpa-onnx-c-api.so` (4.6MB) — C API for Sherpa-ONNX
- `libsherpa-onnx-cxx-api.so` (408KB) — C++ API wrapper
- `libonnxruntime.so` (16.0MB) — ONNX Runtime inference

### Purpose
Provides offline speech recognition when cloud ASR is unavailable. Uses pre-trained ONNX models for:
- Speech recognition (transcription)
- Voice activity detection
- Possibly keyword spotting

## Storage Libraries

### MMKV (libmmkv.so — 718KB)
- Tencent's high-performance key-value store
- Memory-mapped file based
- Used for fast config/preference storage
- `libmmap_wrapper.so` (5KB) companion

### SQLite (libsqlite3.so — 1.5MB)
- Drift ORM (formerly Moor) for structured data
- Hive for lightweight object storage
- Used for: conversation history, health data, translation sessions, cache

## Graphics Libraries

### PDFium (libmodpdfium.so — 4.8MB)
- Chrome's PDF rendering engine
- Used for teleprompter document display
- `libjniPdfium.so` (29KB) JNI bridge

### FreeType (libmodft2.so — 753KB)
- Font rendering for custom Even fonts on glasses display
- Supports TrueType/OpenType

### PNG (libmodpng.so — 249KB)
- PNG image processing for BMP conversion (glasses display format)
