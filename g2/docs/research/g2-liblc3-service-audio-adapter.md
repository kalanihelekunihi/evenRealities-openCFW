# G2 Apollo LC3 service-audio state and lifetime boundary

Status date: 2026-08-30  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Result: bounded software adapter implemented and admitted; stock routing remains
fail-closed

## Result

The admitted LC3 encoder now has a maintained service-facing boundary at
`components/shared/liblc3/runtime_liblc3_service_audio_adapter.[ch]`. It owns
one encoder state, validates the recovered interleaved-PCM geometry, selects
the configured channel, batches complete frames, reports exact completed
output, and bounds open/encode/close operations with a nonzero owner token,
generation, busy state, and integrity seal.

This closes the independently testable state/lifetime adaptation and writable
state placement in software. All four states fit their authenticated stock
slots with no extra RAM. It does **not** make the existing stock header/calls
directly ABI-compatible, place encoder code, rewrite `service_audio`, or emit
firmware.

## Authenticated stock contract

The boundary is limited to behavior visible in the authenticated
`platform\audio\service_audio.c` object at
`[0x0057A900,0x0057B444)`, 2,884 bytes, SHA-256
`01864fb4fc778a70c3c50b7999c8a43b86d4f8763479e8cf5e47d7a529207193`.
The three relevant recovered functions are:

| Function | Range start | Bytes | SHA-256 |
|---|---:|---:|---|
| PCM-width mapper | `0x0057A900` | 38 | `5bbff3fde30dd7e091d8d496ab401b1036e0dc5f158c071b57a0404ed0ace8f0` |
| lazy encoder setup | `0x0057A926` | 26 | `043e57c0075b4e4c1043d93fe1c9cb7fb3abe91ba6ed24af5160a198f7eb3851` |
| `SVC_Lc3EncodeMono` | `0x0057A940` | 568 | `a21f5d12546cd8b00b113b5234e004ca2d6c7deccd2040c3c1d019e81cc5d594` |

The recovered 24-byte configuration fields are PCM format at `+0`, frame
duration at `+4`, encoded sample rate at `+8`, channel count/stride at `+12`,
selected channel at `+16`, and bitrate at `+20`. The stock pointer is at `+24`
and its 2,600-byte encoder storage starts at `+28`.

The adapter preserves the evidenced rules:

- PCM formats 0 through 3 use sample widths 2, 4, 3, and 4 bytes;
- liblc3 receives PCM sample rate zero, which normalizes to encoded rate;
- encoded frames smaller than 20 bytes are unsupported;
- input must contain an exact number of complete interleaved frames;
- multi-channel input advances by a complete frame while the selected channel
  is passed with the original channel count as scalar stride;
- output advances by one encoded frame and reports bytes from completed frames
  if a later frame fails.

No runtime sample rate, duration, bitrate, PCM format, channel count, or
channel selection is assumed. All remain validated at open time.

## ABI and owned lifetime

The Cortex-M55/Arm32 geometry is compile-time asserted:

| Record | Bytes | Alignment/offset |
|---|---:|---:|
| service configuration | 24 | fixed offsets above |
| derived plan | 20 | fixed-width output record |
| compact control header | 28 | seven full-width words |
| complete adapter state | 2,628 | 4-byte aligned |
| storage interval within state | 2,600 | state offset `+28` |
| aligned encoder capacity | 2,596–2,600 | adaptive 0/4-byte prefix |

Before first initialization every control byte preceding storage must be zero;
storage need not be cleared. Initialization is idempotent only for a valid
closed state and cannot reset a live owner. Open rejects owner zero, unknown
PCM geometry, invalid channels, undersized encoded frames, an encoder plan
larger than the slot's aligned 2,596- or 2,600-byte capacity, or provider
setup failure. Encode and close require the same owner. A visible busy state
fails closed under the explicitly single-executor contract.

PCM format, the four provider-admitted frame durations, and the five admitted
sample rates are losslessly coded in one tagged word. Channels, channel
offset, bitrate, owner, and generation remain full-width. On each operation a
64-byte provider view is reconstructed on the stack, its plan is rederived,
and its provider seal is recomputed; the persistent encoder storage is never
reinitialized during encode. A bounded plan-query entry exposes the same
authenticated geometry to the stock-ABI shim without codec setup or state
mutation. The state integrity seal covers the compact
configuration, aligned encoder address/capacity, complete derived plan, owner,
and generation. It therefore rejects geometry or provider tampering before
using attacker-controlled sizes.

Config/plan/output-count pointers and PCM or output buffers may not overlap
adapter state; PCM/output/output-count overlap is also rejected. A provider
error reports the completed prefix and invalidates the lifetime so potentially
mutated codec state cannot be reused without an explicit reopen. Close
invalidates ownership but deliberately does not erase encoder storage.

## Deterministic Cortex-M55 qualification

Two byte-identical builds per reviewed profile compile the adapter, provider,
and all 11 admitted encoder units, then section-GC link from the four adapter
roots. The standalone adapter has no writable data and contains 18 bytes of
read-only duration/rate decoding tables.

| Profile | Adapter object | Text | Retained encoder link |
|---|---:|---:|---:|
| Apple Clang 21.0.0 | 7,072 bytes, `9ad5ccb401ef7e17b6d522ad7fe7671901945efdca8a6d528727fb817e2b02b5` | 2,850 | 185,248 bytes, `7374bd7f371728b51e692192b2ecba901c740784fe77213b72286296b29a5295` |
| Homebrew Clang 22.1.8 | 7,016 bytes, `42495f5e72f3796866e39ebc3eac0dfe5959dd51811af8ec259588e0942dcb94` | 2,810 | 186,092 bytes, `b19de3e9d625a0e04015541992ffd59d2842ed934f5fa97694cea5241dfb747a` |

Each adapter object has exactly 28 relocations: 15 `R_ARM_THM_CALL`, nine
canonical `R_ARM_PREL31` unwind rows, and two MOVW/MOVT address pairs. Its only
undefined symbols are the four
admitted provider entries. Each complete retained link has exactly the
existing 12 runtime imports: `__aeabi_memclr`, `__aeabi_memclr4`, `fabsf`,
`floorf`, `fmaxf`, `fminf`, `memcpy`, `memmove`, `memset`, `roundf`, `sqrtf`,
and `truncf`.

Host tests cover plan-query non-mutation, the complete 80-member
duration/rate/PCM configuration coding grid, all four PCM widths, mono and
interleaved channel geometry, both stock
address phases, multiple-frame cursor advancement, partial provider failure,
reopen, wrong owner, double-open, busy, corrupt state, insufficient
input/output, unsupported configuration, provider setup failure, every
boundary alias, active-owner reset, and retained storage. A second host build
uses the real provider and upstream encoder to prove equal output and retained
encoder lifetime at both stock address phases.

## Remaining routing prerequisites

The four authenticated stock contexts are 2,628 bytes each and contiguous.
The compact adapter state is also exactly 2,628 bytes, so the deficit is zero:
all four states occupy the existing 10,512-byte interval without overlap or
new RAM. Context starts alternate modulo-eight phases four and zero. The
encoder pointer is therefore aligned with alternating zero- and four-byte
prefixes inside the 2,600-byte storage interval, yielding capacities 2,600,
2,596, 2,600, and 2,596 bytes. The maximum adapter-admitted real provider
state is 2,596 bytes, and both phases are exercised by the real-provider host
test.

The five original low-level liblc3 calls cannot target these adapter entries
directly. A separately admitted two-entry stock-ABI shim now binds all nine
whole-image setup/encode ingress sites to the four exact states and performs a
guarded one-way header transition. Production integration must still place
that closure and apply its two authenticated entry tail branches. It must also:

- assign non-overlapping executable/read-only placement;
- bind the 12 runtime imports under their strict relocation contracts;
- compose the encoder's closed 404-byte immutable table policy;
- apply and replay all final relocations; and
- authenticate and rewrite the complete service call path.

The specialized encoder alone remains 30,516 bytes short. The complete Apple
shim/adapter/encoder route is exactly 34,084 bytes short after accounting for
its text and alignment. No stock call
site, overlay, core builder, package manifest, flash plan, or firmware image
was changed. No hardware, acoustic, timing, BLE interoperability, power, or
flash validation was attempted.

## Reproduction

```sh
python3 g2/tools/analyze_g2_liblc3_service_audio_adapter.py --pretty
python3 -m unittest -v g2.tests.test_runtime_liblc3_service_audio_adapter
python3 -m unittest -v g2.tests.test_analyze_g2_liblc3_service_audio_adapter
```

The fail-closed machine-readable receipt is
`components/apollo_main/liblc3_encoder/service_audio_adapter_admission.json`.
