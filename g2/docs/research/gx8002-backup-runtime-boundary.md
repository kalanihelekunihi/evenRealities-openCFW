# GX8002 image-B backup-runtime provider boundary

Current-ledger note: Wave 3 subsequently moved the 36,484-byte image-A XIP
span into the same typed-external category. See
`gx8002-image-a-xip-boundary.md` and `gx8002-source-readiness-ledger.md` for
current totals; the table below preserves this wave's chronological delta.

Status: the largest previously proprietary-unavailable GX8002 span is now an
exact typed external provider boundary. This is a software-only packaging and
identity seam, not executable source recovery and not a production route.

## Authenticated extent

The official G2 2.2.6.10 codec package and the existing stage-two analyzer
close the image-B SRAM text at:

- package `[0x0003B940, 0x0004EE5C)`, 79,132 bytes;
- image-main-segment `[0x323B4, 0x458D0)`;
- IRAM `[0x10003000, 0x1001651C)`;
- vector reset entry `0x10003100`;
- SHA-256
  `cd2ccdc2bca9decff0cc514d3cca6317c28ebdbe22891660f5d9ba00276ecdb3`.

The combined image-B stage-two extent is conclusive. Its internal text/data
split is derived from the last-return sweep, so this boundary deliberately
claims only the authenticated byte extent and identity. It assigns no C
function signatures to internal C-SKY entries.

## Boundary behavior and ownership

`runtime_gx8002_backup_runtime_boundary.[ch]` is original MIT code. It asks an
external provider for exactly 79,132 bytes and uses the shared clean-room
SHA-256 verifier to authenticate the exact body. Missing provider, provider
failure, short output, or digest mismatch fails closed; failed output is
cleared.

No official executable byte is embedded. The underlying C-SKY payload remains
`NOASSERTION` for source license, its redistribution authority remains
unresolved, and the readiness ledger records `production_route=none`.
Provider implementations must independently establish acquisition and
redistribution authority.

The boundary does not make the payload open source. It makes the dependency
explicit and mechanically authenticatable for a local-user-supplied package
workflow.

## Readiness delta

This wave moves one span / 79,132 bytes from
`unavailable_proprietary_codec_firmware` to
`typed_unsupported_external_boundary`:

| Category | Before | After | Delta |
|---|---:|---:|---:|
| Typed external | 120,800 B / 1 span | 199,932 B / 2 spans | +79,132 B / +1 |
| Proprietary unavailable | 205,200 B / 10 spans | 126,068 B / 9 spans | −79,132 B / −1 |
| Source-owned | 0 B | 0 B | 0 |
| Blocking non-metadata | 326,000 B | 326,000 B | 0 |

At this wave boundary, the next largest unavailable span was image-A XIP
text, 36,484 bytes; Wave 3 now closes it as a typed provider seam.

## Verification

```sh
python3 g2/tools/analyze_gx8002_source_readiness.py --json
python3 -m unittest \
  g2.tests.test_gx8002_source_readiness \
  g2.tests.test_gx8002_backup_runtime_boundary \
  g2.tests.test_analyze_g2_codec_stage2_sections
```

Tests exercise the exact local body, mutation, truncation, provider failure,
destination clearing, host and Cortex-M55 compile closure, exhaustive ledger
accounting, and upstream stage-two evidence. No hardware action occurs.

Hardware qualification remains **blocked by unavailable physical evidence**. Future
acceptance retains physical checks for the backup selection policy, IRAM
mapping, and execution behavior.
