# First-party source-replacement frontier ranking

Status: active. This document opens the first-party phase now that every
inferable third-party component is identified
(see [`upstream-inventory.md`](../upstream-inventory.md) and the per-library
audits). Wave-1 item 1 (the transport CRC-32) is now a production
`linux-clang` overlay leaf; the remaining ranking below is forward-looking.
Run addresses use `run = file_offset + 0x00437FE0`.

## Scope

The remaining opaque bytes are first-party Even code. The Apollo-main build tree
holds 233 distinct first-party `.c` files across these subsystems:

| Subsystem | Files | Character |
|---|---:|---|
| `app/gui` | 93 | LVGL-based UI (EvenHub, dashboard, translate/teleprompt, onboarding, menus) |
| `platform/service` | 41 | efs/ota transport, pb_service_* protobuf services, ring/dashboard/settings/time |
| `platform/protocols` | 23 | transport framing, efs/ota, dashboard data, pb services |
| `platform/ble` | 14 | connection/pairing policy, peer manager over Cordio |
| `threads` | 9 | RTOS thread entries |
| `audio` | 6 | PDM/codec DSP |
| `uled`, `ux`, `sync`, `sensor`, `input`, `chg`, `pdm`, `device_mgr`, … | ~40 | drivers and device control |

## What is already source-replaced

First-party replacement is already extensive and proven: a large share of the
591 functions in `components/apollo_main/core_overlay` are first-party Even code
— the UI-module registry event/data dispatch, display-mode and onboarding
policy, the main display-thread loop and its display/BLE senders, the BLE
message-transmit thread and connection state machine, the MRAM
pairing/record database (update/activate/deactivate/query/allocate), the
lens-side status packet reporters, the SARC crash-report helpers, and the
EvenHub RLE/LZ4/IMU layer. The pipeline (disassemble → clean-room source →
overlay leaf → verify) is therefore established for first-party functions, not
only upstream libraries. The new profile-gating mechanism additionally lets an
alternate toolchain take on functions the reviewed apple-clang set has not.

## Ranking of the next first-party waves

Ordered by tractability (self-containment and testability), not importance:

1. **Pure protocol/format computations.** Deterministic, byte-verifiable:
   - the standard reflected CRC-32 (`0xEDB88320`) used by transport-protocol
     packet framing, OTA external-flash verification, and the box-UART manager
     (table at run `0x006987A8`; the table-driven update at run `0x0058FCF0`).
     Distinct from the already-replaced CRC-32C (`efs_crc32c`). **Done —
     production `linux-clang` leaf.** The 40-byte stock update is source-owned
     (`runtime_transport_crc32.c`) and redirected live; see
     [`first-party-transport-crc32-source-boundary-audit.md`](first-party-transport-crc32-source-boundary-audit.md).
   - the CRC-16/CCITT computation (poly `0x1021`, MSB-first), both stock
     variants — XMODEM seed `0x0000` at run `0x0059D350`, and resumable
     CCITT-FALSE seed `*ptr`/`0xFFFF` at run `0x0049ACD4` (48 callers). **Done —
     two production `linux-clang` leaves** (`runtime_crc16_ccitt.c`); see
     [`first-party-crc16-ccitt-source-boundary-audit.md`](first-party-crc16-ccitt-source-boundary-audit.md).
   - packet header pack/unpack (`cmd/NR/TYPE/seq/flags/length/crc32`) framing in
     `transport_protocol.c`. On inspection the send path is a stream/accumulator
     writer with heavy diagnostics rather than a single fixed-layout serializer,
     so it is not a clean standalone leaf; revisit the receive-side parser as a
     candidate. **Deferred.**
   These validate against the firmware byte-for-byte and are ideal first leaves.

2. **Fixed-layout serializers / accessors.** The pb_service_* wrappers around
   nanopb (now identified) marshal Even schemas to protobuf; the fixed field
   packing and the small getters/validators are self-contained.

3. **Device-control state helpers.** Buzzer, LED (`uled`), charger, and RTC
   helpers are small and mostly pure; the RTC calendar path is already partly
   replaced.

4. **UI glue.** `app/gui` is the largest surface but the most LVGL-coupled;
   defer until the LVGL v9.3 boundary is vendored so UI leaves can call source
   LVGL rather than duplicate it.

## Method

Each wave is the established, mechanised pipeline, run on Linux:

1. Focused disassembly to recover the function's exact contract (from the
   memory map, strings, and instruction behaviour).
2. A clean-room `.c` re-expression under `components/apollo_main/core_overlay`.
3. A profile-gated overlay leaf (`"profiles": ["linux-clang"]`) plus a `b_w`
   redirect at the stock address, so the canonical apple-clang overlay stays
   byte-identical while linux-clang carries the replacement.
4. Record the linux-clang pins; `make source verify` reproduces fail-closed.
5. A host/target test validating byte or behavioural equivalence.

Because first-party functions have no upstream oracle, wave 1's pure
computations (which do have a byte-exact firmware oracle — the CRC table and
known check values) are the right place to continue, before moving to
behaviourally-specified Even logic.

This document does not sign, flash, connect to, or mutate hardware.
