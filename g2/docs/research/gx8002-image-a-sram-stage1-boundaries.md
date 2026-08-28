# GX8002 image-A SRAM-text and stage-one provider boundaries

Current-ledger note: Wave 6 subsequently moved image-B stage one (12,288
bytes) and UART boot stage one (10,240 bytes) into the typed-external category.
See `gx8002-stage1-wave6-boundaries.md` and the readiness ledger for current
totals.

Status: Wave 5 closes the largest residual plus the next main-image residual
as exact typed provider seams. Neither seam admits executable source, assigns
internal C-SKY signatures, nor creates a production route.

## Authenticated image-A SRAM text

- package `[0x00015414, 0x000184F8)`, 12,516 bytes;
- stage-two-relative `[0xBE88, 0xEF6C)`;
- IRAM `[0x10023400, 0x100264E4)`;
- reset entry `0x10023500`;
- handler set `0x10023640`, `0x10025574`;
- SHA-256
  `3780ea0bd9c11bb94cd72bfc6a1e8924f2f3e72e9a31ec49a185a18799c9a5f8`.

The vector table and CRT0 evidence close placement and entry addresses. They
do not establish callable C signatures for the body, so none are exposed.

## Authenticated image-A BINH stage-one block

- package `[0x0000958C, 0x0000C58C)`, 12,288 bytes;
- image-A-relative `[0x0000, 0x3000)`;
- CRC-32/MPEG-2 `0x21C58EDB`;
- SHA-256
  `9546164f32680de47fa99ba85ba08a3c538822260957de6c1baee772638da464`.

The public BINH layout and exact vectors authenticate the block. Because the
header load field and vector-address space do not alone prove the complete
ROM copy/remap behavior, this seam deliberately publishes no runtime mapping
or internal ABI.

## Boundary behavior and ownership

Both wrappers are original MIT code over the reviewed exact-segment verifier.
They request their exact lengths, independently verify SHA-256, and clear the
destination on provider failure, truncation, or identity mismatch. They embed
no official executable bytes.

Both underlying payloads remain `NOASSERTION` for source license and unresolved
for redistribution authority. The public MIT container definitions license
format logic, not these official C-SKY bodies. Both ledger rows retain
`production_route=none`.

## Readiness delta

| Category | Before | After | Delta |
|---|---:|---:|---:|
| Typed external | 264,380 B / 4 spans | 289,184 B / 6 spans | +24,804 B / +2 |
| Proprietary unavailable | 61,620 B / 7 spans | 36,816 B / 5 spans | −24,804 B / −2 |
| Source-owned | 0 B | 0 B | 0 |
| Blocking non-metadata | 326,000 B | 326,000 B | 0 |

At this wave boundary the next largest unavailable span was image-B stage one;
Wave 6 now closes it and UART boot stage one as exact provider seams.

## Verification

```sh
python3 g2/tools/analyze_gx8002_source_readiness.py --json
python3 -m unittest \
  g2.tests.test_gx8002_source_readiness \
  g2.tests.test_gx8002_image_a_sram_stage1_boundaries \
  g2.tests.test_analyze_g2_codec_fwpk_segments \
  g2.tests.test_analyze_g2_codec_stage2_sections
```

The software-only tests cover both exact local bodies, independent mutation
rejection, missing/short providers, destination clearing, host and Cortex-M55
object closure, exhaustive accounting, and both parent evidence analyzers.

Hardware qualification remains **blocked by unavailable physical evidence**. Future
acceptance retains physical boot/remap and SRAM execution checks.
