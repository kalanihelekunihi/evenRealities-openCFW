# GX8002 image-A XIP-text provider boundary

Current-ledger note: Wave 4 subsequently moved the 27,964-byte UART boot
stage-two span into the typed-external category. See
`gx8002-uart-boot-stage2-boundary.md` for that delta and
`gx8002-source-readiness-ledger.md` for current totals.

Status: the largest Wave-2 residual is now an exact typed external provider
boundary. This is a clean-room packaging/identity interface, not source
recovery, executable ABI reconstruction, or a production route.

## Authenticated extent

The official G2 2.2.6.10 codec package and existing stage-two analyzer prove:

- package `[0x0000C590, 0x00015414)`, 36,484 bytes;
- image-main-segment `[0x3004, 0xBE88)`;
- SHA-256
  `49c9aed0126493220a3e48827c267d5e94f64d51d9ede0ccc3e84b8946744584`;
- the following SRAM-text offset is exactly `0xBE88` by the public BINH/SPL
  copy formula and the authenticated XIP-length word `0x8E84`.

The public NationalChip grus SDK default XIP base is `0x10200000`, but the
existing audit correctly keeps the build-specific runtime mapping hardware-
deferred. This boundary therefore does not publish a runtime address or
invent signatures for internal C-SKY functions.

## Boundary behavior and ownership

`runtime_gx8002_image_a_xip_boundary.[ch]` is original MIT code. It composes
the reviewed exact-segment verifier, requests exactly 36,484 bytes, and
independently checks SHA-256. Missing provider, provider failure, short
output, or identity mismatch fails closed and clears the destination.

The adapter embeds no C-SKY executable bytes. The payload remains
`NOASSERTION` for source license, redistribution authority remains unresolved,
and the readiness ledger records no production route. An external provider
must establish lawful acquisition and redistribution independently.

## Readiness delta

| Category | Before | After | Delta |
|---|---:|---:|---:|
| Typed external | 199,932 B / 2 spans | 236,416 B / 3 spans | +36,484 B / +1 |
| Proprietary unavailable | 126,068 B / 9 spans | 89,584 B / 8 spans | −36,484 B / −1 |
| Source-owned | 0 B | 0 B | 0 |
| Blocking non-metadata | 326,000 B | 326,000 B | 0 |

At this wave boundary the largest remaining unavailable span was boot stage
two, 27,964 bytes; Wave 4 now closes it as a typed provider seam.

## Verification

```sh
python3 g2/tools/analyze_gx8002_source_readiness.py --json
python3 -m unittest \
  g2.tests.test_gx8002_source_readiness \
  g2.tests.test_gx8002_image_a_xip_boundary \
  g2.tests.test_analyze_g2_codec_stage2_sections
```

Tests cover exact local supply, mutation, truncation, provider failure,
destination clearing, host and Cortex-M55 object closure, exhaustive ledger
accounting, and the existing stage-two evidence. No hardware operation occurs.

Hardware qualification remains **blocked by unavailable physical evidence**. Future
acceptance retains XIP mapping and execution checks without blocking this
software-only classification.
