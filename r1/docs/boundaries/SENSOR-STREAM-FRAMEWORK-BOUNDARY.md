# Unresolved sensor-stream framework boundary

## Disposition

The registration routine at `0x00089890` / 464 executable bytes, noncontiguous timer-dispatch
callback at `0x0008A1E0` / 422 executable bytes, and noncontiguous unregistration routine at
`0x00089B08` / 562 executable bytes form a three-function / 1,448-byte generic named
sensor-stream subscription boundary. They are isolated as
`unknown_sensor_stream_framework_candidate` / `investigate_before_implementing`.

No attributable upstream source, version, or license has been identified. Exact diagnostic-string
searches found no source match, and the body is absent from the pinned Nordic SDK and admitted
third-party snapshots. It is therefore not treated as R1-owned merely because callers use it, and
it is not locally reimplemented.

## Exact noncontiguous body

The contiguous registration body is `0x00089890..<0x00089A60`, has SHA-256
`2c0548e1abf6024d7dcb79b9e1768a9ac4687de976aaa80896ccd6912866e15c`, and is called once at
`0x00089804`. The timer callback Thumb pointer is byte-pinned as `0x0008A1E1`.

The callback body has no direct callsites and is reached through the Thumb pointer stored at
`0x00089ACC`. Its entry range `0x0008A1E0..<0x0008A310` contains 304 bytes and its deferred
cleanup continuation `0x00089BA8..<0x00089C1E` contains 118 bytes. Concatenating the entry range
before the continuation produces 422 bytes with SHA-256
`86e00a0dc3b033c1b4c0ab1414c1fc94b87e0679190ead386c6b2df7f8d444e4`.

The unregistration body is noncontiguous:

| Range | Bytes | Role |
| --- | ---: | --- |
| `0x00089B08..<0x00089B60` | 88 | named-object lookup and missing-object diagnostic |
| `0x00089C20..<0x00089CFA` | 218 | listener lookup, deferred removal, list removal, and cleanup routing |
| `0x0008A068..<0x0008A13E` | 214 | maximum remaining rate, buffer resize, and timer retiming |
| `0x0008A180..<0x0008A1AA` | 42 | final timer release and optional provider close hook |

The four ranges total 562 bytes and have concatenated SHA-256
`6fd417efc7c460d1d8e2a3c234f8fd33b9d04b4324f04f2fcb251a07acefcf3a`. The
decompilation call graph pins 25 direct callsites in 20 caller functions. These span multiple
product/provider domains, including already GoMore-gated `0x00049410` and the R1 motion adapter
`0x0006F228`, which supports a shared-framework boundary rather than attribution to either caller.

## Recovered behavior

Registration caps the listener name at eight bytes and the requested order at one, allocates a
listener record, and appends it to the object's list at offset `0x2C`. The first listener
allocates the shared sample buffer, optionally invokes the provider open hook, and starts the
timer at `1024 / requested_rate`. A later listener with a higher rate resizes the existing buffer
and retimes the timer.

The timer callback obtains the stream object from timer-context offset `0x0C`, validates the
provider read hook and sample-buffer state, reads one fixed sample chunk, and advances or wraps
the shared-buffer cursor. While dispatch bit 1 at object offset `0x28` is set, it walks the
listener list, skips bit-0 deferred-delete entries, and invokes the listener callback at offset
`0x10` according to the listener mode and requested-rate byte. Rate mismatches use the abstract
resize/copy helper at `0x0007D0D8`. After clearing dispatch bit 1, pending-unregister bit 2 routes
to `0x00089BA8`, which removes marked listeners and then retimes or releases the stream resources.

The routine resolves a stream object by name through `0x00089D54`, walks its listener list at
offset `0x2C`, and matches the exact listener pointer. If dispatch is active, it marks the listener
for deferred removal and sets the object's pending-unregister bit. Otherwise it removes and frees
the listener immediately.

When listeners remain, it finds the maximum rate byte at listener offset `0x0D`. If that maximum
falls below the current object rate, it resizes the existing sample buffer through an abstract
allocate/copy/free path and sets the timer period to `1024 / maximum_rate`. When no listeners
remain, it releases the sample buffer and timer, then invokes an optional provider close hook with
the object's stored context.

The exact log strings include `unregister_not_find_obj`, `not_found_in`, and `reset_timer`; they
describe framework behavior but do not identify an author.

## Sharpened fingerprint evidence

The provenance investigation added the following detail. None of it changes the admission state;
the family (32 functions / 2,974 executable bytes) remains `investigate_before_implementing`.

- Exact diagnostic strings, all `[RING]`-tagged with paired un-tagged `nRF_LOG` copies:
  `lisent register fail` (note the typo, at `0x00089A68`), `only support 1 ord`,
  `reset timer,%s, tick:%d`, `register not find obj:%s`, `unregister not find obj:%s`, and
  `%s not found in %s, skip unregister`.
- Health-module initialization creates the stream-object namespace `hr`, `spo2`, `raw_hr`,
  `wear`, `gray`, `aging`, `hrv`, `adt` (plus `temp`, `acc`); listeners are named `wearled`,
  `factory`, `aging`, `detect`, `gomore`, `timing`. Names are capped at eight bytes.
- The stream object is 0x38 bytes with the listener list at offset `+0x2C` and the provider
  vtable at `+0x0C`; the sample buffer is sized `rate * sample_size * 2`.
- Scheduling runs on a 1024 Hz tick with period `0x400 / rate` and a drift-compensated custom
  software-timer list (percent-encoded `d` correction), built only on already attributed FreeRTOS
  heap and Nordic `nRF_LOG` primitives.
- Product-wide reuse across GoMore-gated, R1-motion, factory, and timing callers marks this as
  platform middleware, not a sensor-vendor library.

## Candidates rejected

- Nordic SDK and FreeRTOS `xTimer`: neither provides this named-object/listener registry.
- RT-Thread sensor framework and Zephyr: wrong framework architecture and ecosystem.
- Goodix GH3x2x demo SDK: `Gh3x2x*` naming and log style differ.
- GoMore: a caller of the framework, not its owner.
- Authenticated GitHub code search for all distinctive strings returned zero matches outside this
  project.

## Next evidence step

Cross-reference the companion Android app decompilation (research workspace
`research/apps/even_android_jadx`) for the stream-namespace tokens `raw_hr`, `wearled`, `gray`,
`adt`, and `aging`.

Companion-app search performed 2026-08-13 (negative result): the jadx tree and the installed
native libraries (`libapp.so`, `libeven.so`, `liblc3.so`, both `libjiagu` stages) contain no
occurrence of `raw_hr`, `wearled`, or `lisent`; `gray`/`adt` hits in `libapp.so` are English-word
substrings unrelated to the registry. The stream namespace is firmware-internal only, so the
companion-app route cannot attribute the framework. Combined with the negative cross-firmware
blob scan recorded in `GENERIC-DEVICE-REGISTRY-BOUNDARY.md`, the remaining attribution routes are
authenticated code-host search and acquisition of the platform SDK through the ODM.

## Cross-family interlock

The software-TWI, generic device-registry, RTC-device, time/calendar, and sensor-stream families
interlock: shared positive status enum, runtime registration, and `sys rtc` / `i2c_n` naming.
They most likely form one proprietary platform layer inside Even Realities' B210 product tree and
therefore share one provenance fate.

## Excluded dependencies

This classification does not admit or name the implementations at:

- list operations `0x0005D8E6`, `0x0005D8EE`, `0x0005D998`, and `0x0005D986`;
- allocator/free operations `0x000855A0` and `0x00095D48`;
- sample-buffer resize/copy `0x0007D0D8`;
- timer period/release operations `0x0008A5D0` and `0x0008A3C0`; or
- the indirect provider read, listener callback, open, and close hooks.

A functionally equivalent openR1 subsystem must use already admitted typed sensor-provider and
Nordic/CMSIS primitives. It must not clone this unidentified registry architecture. The static
summarizer reads no live sensor data and exposes no registration or unregistration API.

## Reproduce

```sh
python3 tools/evidence/summarize_r1_sensor_stream_unregister.py
python3 tools/evidence/summarize_r1_sensor_stream_register.py
python3 tools/evidence/summarize_r1_sensor_stream_dispatch.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```

## Attribution re-examination 2026-08

An independent attribution pass (fresh authenticated GitHub code searches for every
distinctive string, general web search, and a line-by-line comparison against both
generations of the MultiTimer software-timer library — the closest public analogue)
found no upstream match. The verdict is unchanged: no attribution; the family remains
proprietary/blocked. Full evidence:
[`unknown_sensor_stream_framework_candidate-ATTRIBUTION-2026-08.md`](unknown_sensor_stream_framework_candidate-ATTRIBUTION-2026-08.md).

Platform-vendor cross-reference (2026-08): the interlocked B210 platform middleware that owns
this family has been identified as Wuxi Bravechip Technologies' "ChipletRing" / BCL603M
smart-ring platform — firmware identity string `603MV1.9.3` and a byte-exact 128-bit GATT
base-UUID match to Bravechip's public `BravechipSpace/ChipletRing-APPSDK`. The platform is
closed-source; this names the commercial acquisition route that would unblock the family.
See `unknown_shared_quantized_neural_runtime_candidate-ATTRIBUTION-2026-08.md`.

## Reduction 2026-08

Under the owner-authorized full reduction (2026-08-14, see
[`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md)), the thirty-two ledger entries of
`unknown_sensor_stream_framework_candidate` (listener registration/unregistration, timer dispatch, buffer resize, and rate retiming) are reconstructed
from the recovered decompilation evidence as independently compiled C in
[`../../reconstructed/sensor_stream/`](../../reconstructed/sensor_stream/).  The
reconstruction is not vendor source; it carries per-function provenance
banners, and its contract, reconstruction decisions, divergences, and
host-test mapping are documented in
[`../correlation/SENSOR-STREAM-REDUCTION-CORRELATION.md`](../correlation/SENSOR-STREAM-REDUCTION-CORRELATION.md).
The ledger disposition for the thirty-two entries is now
`clean_room_reimplementation_owner_authorized`.  This document remains the
provenance record of why no upstream source was admitted.
