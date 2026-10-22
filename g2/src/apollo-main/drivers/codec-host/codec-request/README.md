# Offline codec request packing and channel3 TX

Reconstructed pack0x57BB0A, send0x57C0D6, codecTX0x58FB38 and channel-wrapper0x55E7FA. The channel wrapper calls stock `am_hal_uart_transfer` 0x58E3F8 (upstream AmbiqSuite 5.1.0 unit); its local name `codec_hal_blocking` is a payload defsym alias. No production firmware changes or full driver rebuild claim.

Evidence, mutation tests and bounds (`pre-consolidation:g2/analysis/audio-codec-request-tx-2026-10-09/REPORT.md`). `request.h` documents normal payload limits; this preserves stock malformed-length/null-body behavior and should not be exposed as a hardened application parser. Packing uses shared buffer/sequence and no heap allocation. Physical UART completion and concurrent callers remain unverified.
