# GX8002 volatile UART boot-stage2 provider boundary

Current-ledger note: Wave 5 subsequently moved image-A SRAM text (12,516
bytes) and image-A stage one (12,288 bytes) into the typed-external category.
See `gx8002-image-a-sram-stage1-boundaries.md` and the readiness ledger for
current totals.

Status: the largest Wave-3 residual is now an exact typed external provider
boundary. This preserves authenticated transport and vector facts without
claiming source for the proprietary C-SKY body or adding a production route.

## Authenticated extent and interface

The hash-pinned FWPK/UART-boot analyzer proves:

- package `[0x00002850, 0x0000958C)`, 27,964 bytes;
- type-1 boot-image-relative `[0x2820, 0x955C)`;
- load address `0x10002800`;
- reset vector `0x10002900`;
- remaining vector-handler set `0x10002994`, `0x10003124`;
- byte-sum checksum `0x0024D441` from the public boot header;
- SHA-256
  `4aacc9e5bf45001bef99785b62302e88bd0b5e6bf4d6186fd7033b1eaeb05b0d`.

The image is streamed to volatile GX8002 IRAM during DFU. Vector identities
prove placement and entry addresses but do not establish C signatures,
interrupt-frame layout, or internal service semantics. None are invented by
this boundary.

## Boundary and licensing

`runtime_gx8002_uart_boot_stage2_boundary.[ch]` is original MIT code. It asks
an external provider for exactly 27,964 bytes and composes the reviewed local
SHA-256 verifier. Missing provider, provider error, short output, or digest
mismatch fails closed and clears the supplied destination.

The provider seam embeds no C-SKY firmware bytes. The stage-two payload stays
`NOASSERTION` for source license, its binary redistribution authority remains
unresolved, and `production_route` remains `none`. The MIT-licensed public
NationalChip UART container format supports the interface classification but
does not license this official executable body.

## Readiness delta

| Category | Before | After | Delta |
|---|---:|---:|---:|
| Typed external | 236,416 B / 3 spans | 264,380 B / 4 spans | +27,964 B / +1 |
| Proprietary unavailable | 89,584 B / 8 spans | 61,620 B / 7 spans | −27,964 B / −1 |
| Source-owned | 0 B | 0 B | 0 |
| Blocking non-metadata | 326,000 B | 326,000 B | 0 |

At this wave boundary, the largest remaining unavailable span was image-A
SRAM text; Wave 5 now closes it and image-A stage one as provider seams.

## Verification

```sh
python3 g2/tools/analyze_gx8002_source_readiness.py --json
python3 -m unittest \
  g2.tests.test_gx8002_source_readiness \
  g2.tests.test_gx8002_uart_boot_stage2_boundary \
  g2.tests.test_analyze_g2_codec_fwpk_segments
```

The suite covers exact local supply, mutation, truncation, provider failure,
destination clearing, host and Cortex-M55 object closure, exhaustive ledger
accounting, and independent FWPK/vector evidence. It performs no hardware
operation.

Hardware qualification remains **blocked by unavailable physical evidence**. Future
acceptance retains the physical UART boot and execution checks.
