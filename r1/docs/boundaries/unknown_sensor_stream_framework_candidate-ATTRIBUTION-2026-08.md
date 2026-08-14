# Attribution re-examination: `unknown_sensor_stream_framework_candidate` (2026-08)

Companion to [`SENSOR-STREAM-FRAMEWORK-BOUNDARY.md`](SENSOR-STREAM-FRAMEWORK-BOUNDARY.md).
This report records a fresh, independent attribution pass over the family. It changes no
admission state: the family remains `investigate_before_implementing`.

## Family under test

- **Family**: `unknown_sensor_stream_framework_candidate`
- **Size**: 32 functions / 2,974 executable bytes (per `r1/docs/reference/FUNCTION-OWNERSHIP.csv`)
- **Address ranges**:
  - `0x0005D8FE..0x0005D997` — offset-intrusive list container helpers
    (`FUN_0005d8fe` descriptor init, `FUN_0005d90e` pool-node allocate+insert,
    `FUN_0005d986` idle check);
  - `0x0007D0D8..0x0007D153` — abstract sample-buffer resize/copy helper;
  - `0x000896F0..0x0008A5FB` — the framework bulk: stream-object create (`0x000896F0`),
    register-by-name wrapper (`0x000897E8`), listener registration (`0x00089890`, 464 B),
    unregistration (`0x00089B08`, 562 B, noncontiguous), name lookup (`0x00089D54`),
    object-list insert (`0x00089D9C`), result-staging slots (`0x00089E50`/`0x00089E8C`/
    `0x00089EC8`/`0x00089ED8`/`0x0008A03C`), timer dispatch (`0x0008A1E0`, 422 B,
    noncontiguous), and the custom software-timer layer (`0x0008A310`, `0x0008A368`,
    `0x0008A3C0`, `0x0008A3F0`, `0x0008A404`, `0x0008A45C`, `0x0008A540`, `0x0008A55C`,
    `0x0008A584`, `0x0008A5C0`, `0x0008A5D0`, `0x0008A5E4`).

## Methods

1. Read the existing boundary doc and the ledger evidence strings; did not repeat its
   negative results blindly — re-ran the code-host searches with fresh queries (below).
2. Re-read the decompiled bodies of all principal family functions in
   `r1/research/decompilation/application/decompiler-output.c` (register `0x00089890`
   line 102152, unregister `0x00089B08` line 102298, dispatch `0x0008A1E0` line 102789,
   object create `0x000896F0` line 102039, timer layer `0x0008A310..0x0008A5E4` lines
   102991–103374, list helpers lines 54407–54547) plus callers via `call-graph.csv`-style
   grep over the decompilation.
3. Authenticated GitHub code search (`gh api search/code`) for every distinctive exact
   string, and general web search for the same strings and the vendor hypothesis.
4. Fetched and compared the actual upstream source of the closest-matching open-source
   software-timer library (MultiTimer) line-by-line against the decompiled timer layer.

## Structural fingerprint (recovered from bodies)

The framework is a bespoke named-stream publish/subscribe middleware plus a custom
software-timer layer:

- **Stream object** (0x38 bytes, `FUN_000896f0`): name (8-byte cap) at +0x00, provider
  vtable at +0x0C (`open` at slot 0, `close` at slot 4, `read` at slot 8), current rate
  byte at +0x10, sample buffer at +0x14 sized `rate * sample_size * 2`, cursor at +0x18,
  sample size at +0x1C, timer at +0x20, provider context at +0x24, flags at +0x28
  (bit0 = static-object, bit1 = dispatch-active, bit2 = pending-unregister), listener
  list descriptor at +0x2C.
- **Listener record**: stream back-pointer +0x00, name (8-byte cap) at +0x04, user pointer
  +0x0C, requested-rate byte +0x0D, mode byte +0x0E (`0` = full-buffer, `1` = per-chunk),
  callback +0x10, flags +0x14 (bit0 = deferred-delete, bits 1..15 = decimation phase
  counter). Registration clamps the "order" argument to 1 (`only support 1 ord`).
- **Scheduling**: 1024 Hz tick, period `0x400 / rate`; per-listener rate decimation by a
  15-bit phase counter folded into the listener flags word (dispatch at
  `0x0008A1E0`, lines 102858–102866).
- **Software timer** (`FUN_0008a310`): heap node from the offset-intrusive list pool;
  fields {period +0x00, start-tick +0x04, callback +0x08, context +0x0C,
  repeat-count +0x10 initialized to `0xFFFFFFFF` (infinite), flags +0x14 (bit0 = stopped,
  bit1 = auto-remove-on-expiry)}. The poll loop (`FUN_0008a45c`, line 103165) expires
  timers by remaining-time underflow, decrements repeat, defers removal, computes the
  minimum remaining time for next wakeup, and every ≥500 ticks applies a drift
  correction: `correction = 'd'(=100) - (elapsed*100/span)` at lines 103214–103224.
- **Log style**: every diagnostic exists in two copies — a `[RING]`-tagged copy routed
  through the product log macro and an un-tagged `nRF_LOG` copy — i.e. the framework was
  integrated with a dual-backend log shim, typical of vendor middleware dropped into the
  product tree.

## Hypotheses tested

### H1 — Exact-string code-host attribution (re-run, authenticated)

Fresh `gh api search/code` queries, 2026-08-14:

| Exact query | Hits | Assessment |
|---|---:|---|
| `"lisent register fail"` | 0 | no public source |
| `"unregister not find obj"` | 0 | no public source |
| `"register not find obj"` | 0 | no public source |
| `"reset timer,%s, tick:%d"` | 0 | no public source |
| `"not found in" "skip unregister" language:c` | 0 | no public source |
| `"only support 1 ord"` | 4 | all unrelated (Hyperledger Go tooling, TSX UI text) |
| `"obj malloc fail"` | 52 | all unrelated (ESP8266 `spi_ram_fifo.c`, etc.) |
| `"list_insert_fail"` | 206 | all unrelated (ESP SPI RAM, etc.) |
| `"wearled"` | 310 | all substring noise (`MetaWearLED`, OCR corpora) or this repo/mirror |
| `"raw_hr" "gomore"` | 20 | only this repository and its mirror |

General web search for the same strings returned only unrelated noise. This independently
reproduces the boundary doc's negative code-host result with fresh queries.

### H2 — MultiTimer (0x1abin) software timer — tested HARD, NO MATCH

The firmware timer layer superficially resembles the popular MIT-licensed Chinese-embedded
library MultiTimer (heap nodes, callback + userData, repeat semantics, yield-style poll).
Both upstream generations were fetched and compared:

- v1 (`master`/`legacy`, Copyright 2016 Zibin Zheng,
  https://github.com/0x1abin/MultiTimer/blob/legacy/multi_timer.c): statically allocated
  `struct Timer {cur_ticks, cur_expired_time, timeout, repeat, arg, timeout_cb, next}`
  in a singly-linked list; `timer_loop()` re-arms via `cur_expired_time = repeat` and
  removes on `repeat == 0`. No heap pool, no offset-intrusive list, no repeat *count*
  (`-1` = infinite) semantics, no deferred free, no min-remaining computation, no drift
  correction.
- v2 (`main`, https://github.com/0x1abin/MultiTimer/blob/main/MultiTimer.c):
  deadline-sorted singly-linked list; `multiTimerYield()` pops only list-head expiries;
  no repeat count at all, no flags word, no drift compensation.

The firmware layer (`FUN_0008a310`/`FUN_0008a404`/`FUN_0008a45c`) differs in every
structural dimension: offset-intrusive doubly-linked pool list, `repeat = 0xFFFFFFFF`
countdown at node +0x10, stopped/auto-remove flag bits at +0x14, deferred free through
`FUN_0008a3c0`, full-list minimum-remaining scan, and a percent drift corrector keyed on
`'d'` (100). **Verdict: no match — not MultiTimer or any recognizable derivative.**

### H3 — Vendor platform SDK hypotheses

- **Goodix GH3x2x demo SDK / GoMore SDK**: previously rejected (naming and log style
  `Gh3x2x*` differ; GoMore is a *caller* — listener names include `gomore`). No new
  evidence contradicts this; the framework's callers span GoMore-gated, R1-motion,
  factory, and timing domains, which marks it as platform middleware, not a
  sensor-vendor or algorithm-vendor library.
- **HRS3300 / PAH800x sensor-hub SDKs**: these ship bare sensor drivers plus algorithm
  blobs; none publish a named-stream listener registry, and the same framework schedules
  non-PPG streams (`acc`, `temp`, `timing`), which is out of scope for any single PPG
  vendor. Not plausible; no source available to compare — treated as rejected by scope.
- **Jieli / Bluetrum / Realtek smartwatch SDKs**: all target their own SoCs with their
  own RTOS/HAL; none would appear as FreeRTOS + `nRF_LOG` + nRF52840 middleware, and no
  string from their public SDK trees matches (H1). Rejected.
- **RT-Thread sensor framework / Zephyr / Nordic SDK / FreeRTOS `xTimer`**: prior
  rejections stand; the architecture (name-keyed stream objects, listener decimation,
  bespoke timer) exists in none of them.

### H4 — Vendor identification via local strings/paths

No file paths, copyright markers, or author identifiers exist anywhere near the family in
the decompilation or `symbols.csv` (all nearby symbols are `DEFAULT`-source Ghidra
labels — the image carries no debug info). The only product marker remains the `[RING]`
log tag, which is product-level, not framework-level. The stream namespace
(`hr`, `spo2`, `raw_hr`, `wear`, `gray`, `aging`, `hrv`, `adt`, `temp`, `acc`) and
listener names (`wearled`, `factory`, `aging`, `detect`, `gomore`, `timing`) are
firmware-internal only (companion-app route already exhausted per the boundary doc).

### H5 — Cross-family interlock (unchanged, reaffirmed)

The interlock documented in the boundary doc and in
[`GENERIC-DEVICE-REGISTRY-BOUNDARY.md`](GENERIC-DEVICE-REGISTRY-BOUNDARY.md) /
[`SOFTWARE-TWI-PROVIDER-BOUNDARY.md`](SOFTWARE-TWI-PROVIDER-BOUNDARY.md) stands: the
gap-free positive status enum `0..12` shared with the software-TWI adapters and the
generic device registry, runtime registration into shared records, and the
`sys rtc` / `i2c_n` device naming all indicate one proprietary platform layer by one
author (the B210 product tree's ODM platform team). Whatever resolves one family resolves
all of them.

## Final verdict

**(c) NO ATTRIBUTION — remains proprietary/blocked.**

No upstream open-source library, version, or license could be established for any part of
the family. The closest public analogue (MultiTimer) was fetched and rejected on
line-by-line structural comparison. Authenticated GitHub code search and general web
search confirm that every distinctive string (`lisent register fail`, `only support
1 ord`, `reset timer,%s, tick:%d`, `register/unregister not find obj:%s`,
`%s not found in %s, skip unregister`, `obj malloc fail`, `list_insert_fail`) and every
namespace token (`raw_hr`, `wearled`) exists in no public codebase other than this
project and its mirror.

The family remains `unknown_sensor_stream_framework_candidate` /
`investigate_before_implementing`. Remaining attribution routes, unchanged from the
boundary doc: acquisition of the ODM platform SDK, or future appearance of the platform
in a public leak/release. Do not clone this architecture; the admitted replacement path
(typed sensor-provider + Nordic/CMSIS primitives) stands.
