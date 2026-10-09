# Offline codec request packing and channel3 TX

Reconstructed pack0x57BB0A, send0x57C0D6, codecTX0x58FB38 and channel-wrapper0x55E7FA. `hal_bridge.c` includes unchanged sealed selected SDK UART text and exposes its private blocking body through only the validated type0/handle-validation contract. No production firmware changes or full driver rebuild claim.

[Evidence, mutation tests and bounds](../../../analysis/audio-codec-request-tx-2026-10-09/REPORT.md). `request.h` documents normal payload limits; this preserves stock malformed-length/null-body behavior and should not be exposed as a hardened application parser. Packing uses shared buffer/sequence and no heap allocation. Physical UART completion and concurrent callers remain unverified.
