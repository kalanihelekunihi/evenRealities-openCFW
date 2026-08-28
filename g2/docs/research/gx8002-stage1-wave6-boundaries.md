# GX8002 image-B and UART stage-one provider boundaries

Current-ledger note: Wave 7 subsequently classified the final 14,288 bytes
(gxNPU commands and two runtime-data spans) as typed external boundaries. See
`gx8002-wave7-final-boundaries.md` and the readiness ledger for current totals.

Status: Wave 6 closes both remaining stage-one executable bodies as exact
typed provider seams. No executable source, internal C-SKY ABI, or production
route is claimed.

## Image-B BINH stage-one block

- package `[0x0003893C, 0x0003B93C)`, 12,288 bytes;
- main-image-relative `[0x2F3B0, 0x323B0)`;
- CRC-32/MPEG-2 `0xA582510C`;
- SHA-256
  `a80924ccf78205ef1761c4f568d4ce31f909635bf3ad7eecfaed250ad801626c`.

The public BINH layout, exact vectors, block CRC, and SHA prove identity. They
do not fully specify ROM copy/remap behavior, so no runtime mapping or callable
function signature is exposed.

## Volatile UART boot stage one

- package `[0x00000050, 0x00002850)`, 10,240 bytes;
- boot-image-relative `[0x0020, 0x2820)`;
- IRAM load `0x10000000`;
- reset vector `0x10000100`;
- trap-vector set `0x10000130`, `0x10000134`;
- SHA-256
  `cbbe85a2d60f5bb805dddb45fa2eac1632bdf0ab80665c040c0892c64074133f`.

These are placement and vector facts, not C ABI evidence. The body remains
opaque and externally supplied.

## Boundary behavior and ownership

Both wrappers are original MIT code over the reviewed exact-segment SHA-256
verifier. Missing, failing, truncated, or identity-mismatched providers fail
closed and their destination is cleared. No official byte is embedded.

Underlying payload source licenses remain `NOASSERTION`, redistribution
authority remains unresolved, and production routes remain absent. The public
MIT container definitions do not relicense either official executable body.

## Readiness delta

| Category | Before | After | Delta |
|---|---:|---:|---:|
| Typed external | 289,184 B / 6 spans | 311,712 B / 8 spans | +22,528 B / +2 |
| Proprietary unavailable | 36,816 B / 5 spans | 14,288 B / 3 spans | −22,528 B / −2 |
| Source-owned | 0 B | 0 B | 0 |
| Blocking non-metadata | 326,000 B | 326,000 B | 0 |

At this wave boundary the largest unavailable span was the 9,164-byte gxNPU
command stream; Wave 7 now closes it and both remaining data spans.

## Verification

```sh
python3 g2/tools/analyze_gx8002_source_readiness.py --json
python3 -m unittest \
  g2.tests.test_gx8002_source_readiness \
  g2.tests.test_gx8002_stage1_wave6_boundaries \
  g2.tests.test_analyze_g2_codec_fwpk_segments
```

The suite covers both exact local spans, independent mutation rejection,
missing/short providers, destination clearing, host/Cortex-M55 import graphs,
exhaustive accounting, and parent container evidence. It is software-only.

Hardware qualification remains **blocked by unavailable physical evidence**. Future
acceptance retains physical boot, remap, and execution checks.
