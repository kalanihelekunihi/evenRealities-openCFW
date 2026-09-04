# G2 audio service-algorithm recovery

## Result

The retained `platform\audio\service_algo.c` object is closed as ten functions
at `[0x005915DC, 0x00591D14)`. The object is 1,848 bytes with SHA-256
`192014709d2eb4d2060037484a59e6594b0aabe7044c99a340da8070b9256322`:
1,712 executable bytes and a 136-byte literal/constant pool. All ten functions
were already present in the authenticated Ghidra corpus; the original retained
path anchored only the preprocessing and SSR functions.

No NationalChip, codec-vendor DSP, or other third-party signal-processing body
is linked. The signal algorithm is G2 first-party code. Its reusable edges are
ten bounded IAR DLIB/compiler-runtime calls—three `memset`, one `asin`, four
signed-64-to-double conversions, and two hardware-backed `sqrt` calls—plus six
calls to the already production source-owned ARM EABI unsigned 64-bit division
core. Logging terminates at the admitted EasyLogger/private compact-log seams.

The object provides no new IAR version discriminator and no private historical
commit. OpenCFW now production-routes all ten stock entries to a clean-room,
freestanding C implementation under strict Apple-Clang and Linux-Clang
relocation contracts. The 1,712 stock body bytes are functionally displaced;
the canonical image retains 1,809 physical compatibility bytes (including the
136-byte pool) because the guarded four-byte entry branches make the old bodies
unreachable. Of those entry bytes, 39 differ from the authenticated image.

## Reproduction

Run:

```sh
make service-algo-closure
```

The fail-closed analyzer authenticates the official image, all function bodies,
the physical object and both boundaries, M-profile/VFP instruction topology,
calls and ingress, retained strings, production ownership of 64-bit division,
the exact stock bodies for IAR `asin`, signed-64-to-double conversion, and
hardware-backed `sqrt`, all ten source leaves and guarded redirects, both
toolchain profiles, strict relocations, the live Apple build, and the canonical
manifest tiling. The Make target also runs host behavioral tests and a
freestanding Cortex-M55 hard-float compile.

| Evidence | Result |
|---|---:|
| Linked / Ghidra-discovered functions | 10 / 10 |
| Path-anchored functions | 2 |
| Raw path references / referencing functions | 3 / 2 |
| Body bytes | 1,712 |
| Pool bytes | 136 |
| Physical bytes | 1,848 |
| Reachable instructions | 574 |
| Direct calls | 43 |
| Internal / external direct calls | 12 / 31 |
| Indirect calls | 0 |
| Whole-image direct `BL` entries | 15 |
| Stored / strict-interior entries | 0 / 0 |

The body SHA-256 is
`3305e7f03d2467f82f7eee882a91a397175e7d8f83c2b7c182eb814d559fac78`.
The instruction topology digest is
`c498644a69a2a0eaaeafb8a2104feacc0daaab776442fd5656994f957c0bae7d`,
and the direct-call digest is
`028d48f20b6996de8a5b761340193d872ee91672cc7e711ac23a7e2ffb477673`.

## Recovered algorithm

The top-level processing path operates on 800 interleaved stereo frames:

1. split the left and right 16-bit channels into two 1,600-byte working
   buffers;
2. produce a third 16-bit mono buffer as half-left plus half-right;
3. accumulate signed 64-bit sum-of-squares for both channels;
4. divide each energy by 800;
5. compare the current combined energy with a rolling ten-window baseline;
6. cross-correlate the two channels over lags `-10...+10`;
7. apply energy and correlation thresholds; and
8. convert the selected normalized delay through `asin` to signed degrees.

The ten functions cover buffer access, preprocessing, SSR ratio calculation,
quiet-NaN/no-op floating helpers, delay-to-angle conversion, cross-correlation,
source-angle calculation, the top-level two-short output wrapper, and rolling
energy-window update.

## Input-size compatibility hazard

`algo_front_data_preprocess` rejects null input, sizes not divisible by four,
and sizes greater than 3,200 bytes. It does **not** require the size to equal
3,200. After that check it unconditionally loops over 800 stereo frames and
therefore reads exactly 3,200 input bytes.

So a short but four-byte-aligned input is accepted and then read beyond its
declared extent. The OpenCFW production implementation instead requires exactly
3,200 bytes and rejects short input before dereferencing it. Host tests pin this
fail-closed behavior as well as null outputs, silence/energy rejection, lag
selection, angle conversion, and ten-window wraparound.

## IAR math seam

The exact called helper bodies are:

| Entry / span | Bytes | Identification | SHA-256 |
|---|---:|---|---|
| `[0x0043C260,0x0043C36E)` | 270 | double `asin` implementation | `b69e1f84d2bade8702adfb2fd50ac4cb218a8d50af0fbc28a9c8f92d7692b558` |
| `[0x0059C7AC,0x0059C800)` | 84 | signed 64-bit integer to IEEE-754 double | `eebedaca845140b15ab5ffbe3ed94e135d303dc976ac2e5d320bcdb7e4d0b596` |
| `[0x0059C800,0x0059C81C)` | 28 | VFP `VSQRT.F64` with negative-input errno path | `dbb01d401deb7e25eb46eaa901dfae2231f08896ef1eb4ab488c1cc61c2a35bd` |

These semantics are sufficient to source-recreate the narrow behavior or to
retain bounded official seams. They do not distinguish a specific IAR release
beyond the established EWARM 9.20+ floor and 9.60.2 leading compatibility
candidate.

The six unsigned 64-bit division calls reach `0x0047CC60`, which is already an
exact production redirect to `open_cfw_aeabi_uldivmod`. No opaque division or
DSP library remains at that edge.

## OpenCFW production status

The admitted source implements the first-party fixed-window correlation and
energy policy, uses the existing source-owned 64-bit division core, and carries
bounded source-owned square-root and arcsine approximations so the firmware has
no new hosted-libm dependency. Apple Clang emits 4,762 text bytes plus 14 bytes
of alignment; Linux Clang emits 4,774 text bytes plus 12 bytes of alignment.
Each profile has 20 strict relocations and the same ten guarded stock-entry
redirects. The software functional gap is closed.

Acoustic equivalence, actual G2 microphone spacing and polarity, and live
lag-to-angle behavior require an authorized physical G2 pair or authenticated
golden microphone vectors. Hardware validation is **blocked by unavailable
physical evidence**. This is a hardware-qualification blocker, not a remaining
software implementation gap.

No device, signing, flashing, erase, or runtime operation was performed.
