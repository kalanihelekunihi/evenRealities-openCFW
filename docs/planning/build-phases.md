# Build Phases — Completed Work History

Completed firmware-only reverse engineering phases, moved from PLAN.md per the continuous iteration policy.

---

## Phase 1: Scope Lock and Evidence Baseline (2026-03-03)
- Froze analysis boundaries to local firmware + local docs only.
- Listed in-scope directories (`captures/firmware/`, `docs/`) and documentation targets.
- Established traceability template: every conclusion references file path + offset/string/signature evidence.

## Phase 2: Firmware Corpus Inventory and Fingerprinting (2026-03-03)
- Enumerated all firmware packages/components across 5 versions (v2.0.1.14, v2.0.3.20, v2.0.5.12, v2.0.6.14, v2.0.7.16).
- Recorded file metadata, hashes, sizes, magic bytes, and inferred format type.
- Built version/component matrix showing which binaries exist per release.
- **Artifacts**: `captures/firmware/analysis/2026-03-03-firmware-corpus-baseline.{md,json}`, `tools/build_firmware_corpus_baseline.py`

## Phase 3: Container and Header Mapping (2026-03-03)
- Reverse engineered EVENOTA package header and 6-entry TOC format.
- Identified field semantics: magic (8 bytes), entry count (LE32), build date/time (16 bytes each), version (36 bytes), per-entry: id/offset/size/checksum (4×LE32).
- Validated parsed structure against real byte boundaries and extraction outputs.
- **Artifacts**: `captures/firmware/analysis/2026-03-03-evenota-header-validation.{md,json}`, `tools/validate_evenota_headers.py`

## Phase 4: Component Decomposition (2026-03-03)
- Analyzed all 6 extracted components: bootloader, firmware_ota (main app), BLE (EM9305), touch (CY8C4046FNI), codec (GX8002B), box (case MCU).
- Identified architecture hints: ARM Cortex-M55 vector tables, IAR EWARM build paths, LVGL v9.3, FreeRTOS, Cordio BLE.
- Documented component roles and boot/update relationships.
- **Artifacts**: `captures/firmware/analysis/2026-03-03-firmware-component-decomposition.{md,json}`, `tools/analyze_firmware_components.py`

## Phase 5: Integrity, Packaging, and Update Semantics (2026-03-03)
- Validated CRC32C checksums across all versions (all pass).
- Mapped OTA packaging order: codec(4) → BLE(5) → touch(3) → box(6) → bootloader(1) → main_app(0).
- Identified sub-component wrapper formats: FWPK (codec, touch), segmented patch (BLE), EVEN header (box), 32-byte preamble (main app).
- **Artifacts**: `captures/firmware/analysis/2026-03-03-integrity-packaging-semantics.{md,json}`, `tools/analyze_integrity_packaging.py`

## Phase 6: Bluetooth Artifact Extraction (2026-03-03)
- Mined 13 BLE-related UUIDs, 9 AT commands (AT^COMB, AT^DEVNAME, AT^EM9305, etc.).
- Mapped transport framing clues: packet envelope (AA prefix, CRC16), file transfer opcodes (0xC4/0xC5).
- Identified command families: auth (0x80), display (0x04/0x06/0x0E/0x81), file (0xC4/0xC5), config (0x0D), EvenAI (0x07).
- **Artifacts**: `captures/firmware/analysis/2026-03-03-ble-artifact-extraction.{md,json}`, `tools/analyze_ble_artifacts.py`

## Phase 7: Hardware Functionality Mapping (2026-03-03)
- Correlated component evidence to 6 hardware subsystem boundaries: SoC, BLE radio, display, audio codec, touch, case MCU.
- Inferred subsystem responsibilities with confidence levels (confirmed/likely/unknown).
- Identified inter-component communication: MSPI (display), I2C (touch DFU, sensors), TinyFrame serial (codec), HCI (BLE), wired UART/I2C (inter-eye).
- **Artifacts**: `captures/firmware/analysis/2026-03-03-hardware-functionality-mapping.{md,json}`, `tools/analyze_hardware_mapping.py`

## Phase 8: Cross-Version Diff and Behavior Evolution (2026-03-03)
- Diffed 5 firmware versions, identified: BLE (byte-identical across all), codec (stable), touch (+22.6% at v2.0.6.14), box (small growth), main app (significant evolution).
- Highlighted BLE-facing stability: EM9305 patches unchanged → no protocol-breaking BLE changes.
- Captured regression risk: touch firmware growth suggests new gesture capabilities; main app changes suggest ANCS support added in v2.0.6.14+.
- **Artifacts**: `captures/firmware/analysis/2026-03-03-cross-version-behavior-evolution.{md,json}`, `tools/analyze_cross_version_evolution.py`

## Phase 9: Documentation Reconciliation and Update (2026-03-03)
- Reconciled all claims in `docs/firmware/firmware-reverse-engineering.md` against Phase 6-8 evidence, tagged with confidence levels.
- Added §23.8 "Binary Analysis Evidence Index" mapping phase artifacts to validated claims.
- Added §23.9 "Corrections from Prior Assumptions" (10 corrected/refined claims: nRF52840→Apollo510b, S140→Cordio, etc.).
- Created `docs/firmware/ota-protocol.md` — complete BLE wire protocol for firmware transfer.
- Updated `docs/firmware/README.md` with ota-protocol.md reference.

## Phase 10: Validation, Gaps, and Next Firmware-Only Backlog (2026-03-03)
- Ran full reproducibility sweep: all 7 Phase 1-8 analysis tools compile and produce valid JSON outputs.
- Enumerated unresolved firmware-only unknowns (see §22 of firmware-reverse-engineering.md).
- Published next-wave backlog in PLAN.md Continuation Backlog.

---

## Reproducible Validation Commands (Phase 10.1)

All 7 tools verified: compile (py_compile) → run → valid JSON output.

```bash
# Phase 2 — Corpus baseline
python3 tools/build_firmware_corpus_baseline.py

# Phase 3 — EVENOTA header validation
python3 tools/validate_evenota_headers.py

# Phase 4 — Component decomposition
python3 tools/analyze_firmware_components.py \
  --output-md captures/firmware/analysis/2026-03-03-firmware-component-decomposition.md \
  --output-json captures/firmware/analysis/2026-03-03-firmware-component-decomposition.json

# Phase 5 — Integrity & packaging
python3 tools/analyze_integrity_packaging.py \
  --output-md captures/firmware/analysis/2026-03-03-integrity-packaging-semantics.md \
  --output-json captures/firmware/analysis/2026-03-03-integrity-packaging-semantics.json

# Phase 6 — BLE artifact extraction
python3 tools/analyze_ble_artifacts.py \
  --output-md captures/firmware/analysis/2026-03-03-ble-artifact-extraction.md \
  --output-json captures/firmware/analysis/2026-03-03-ble-artifact-extraction.json

# Phase 7 — Hardware mapping
python3 tools/analyze_hardware_mapping.py \
  --output-md captures/firmware/analysis/2026-03-03-hardware-functionality-mapping.md \
  --output-json captures/firmware/analysis/2026-03-03-hardware-functionality-mapping.json

# Phase 8 — Cross-version evolution
python3 tools/analyze_cross_version_evolution.py \
  --output-md captures/firmware/analysis/2026-03-03-cross-version-behavior-evolution.md \
  --output-json captures/firmware/analysis/2026-03-03-cross-version-behavior-evolution.json
```
