# GX8002 codec/DSP source-readiness ledger

Status: the official G2 2.2.6.10 codec package now has an exhaustive,
non-overlapping 17-span readiness partition. The largest independently
actionable opaque cluster, the 120,800-byte keyword-spotting weight region,
is closed as a typed MIT provider boundary. It is not source-admitted and is
not production-routed.

The deterministic analyzer is
`tools/analyze_gx8002_source_readiness.py`; the byte ledger is
`tools/manifests/gx8002-source-readiness.tsv`; the boundary is
`components/shared/gx8002/runtime_gx8002_kws_model_boundary.[ch]`.

## Whole-package accounting

The input is the authenticated official package
`firmware_codec.bin`, 326,092 bytes, SHA-256
`b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0`.
Every byte belongs to exactly one ledger row:

| Readiness | Spans | Bytes | Meaning |
|---|---:|---:|---|
| Reconstructible MIT format metadata | 6 | 92 | Public FWPK/BINH fields or deterministic alignment fill; this does not license official package bytes |
| Typed unsupported external boundary | 11 | 326,000 | Every non-metadata span has an exact authenticated provider ABI; payload source and redistribution remain external |
| Proprietary codec firmware unavailable | 0 | 0 | No byte remains unclassified; unsupported payloads remain blocking through their typed boundaries |
| **Total** | **17** | **326,092** | Exact contiguous partition, zero gaps or overlaps |

Source-owned firmware bytes remain **zero**. The 92 metadata bytes are a
format-reconstruction category, not a claim that the official bytes may be
redistributed. Blocking content remains 326,000 bytes: the typed boundaries
make all 326,000 bytes explicit and safely injectable, but do not turn them into
open source.

## Selected cluster: KWS weights

The existing stage-two closure independently proves:

- package extent `[0x0001B15C, 0x0003893C)`, 120,800 bytes;
- image-A stage-two-relative extent `[0x11BD0, 0x2F3B0)`;
- SHA-256
  `397971427d7097180d07eb63f9822904a555e51f7643d946ebb38d71a967f8cf`;
- decoded DRAM staging address `0x200056D0`;
- the size getter and exact fit at the image-B boundary.

These facts authenticate the region but do not establish who trained the
model, its source dataset, its source form, or permission to redistribute
the model. The weight payload therefore remains `NOASSERTION` for source
license and unresolved for redistribution authority.

The clean-room MIT boundary accepts an explicit user/provider callback,
requests exactly 120,800 bytes, computes SHA-256 locally, and accepts only
the authenticated identity above. A missing provider returns unsupported.
Provider failure, short output, or digest mismatch fails closed and clears
the destination. The adapter embeds no model bytes and adds no production
route. Acquisition and authorization remain responsibilities of the
external provider.

## Attribution boundary

The FWPK, UART boot, and BINH layouts are attributable at interface level to
the MIT-licensed public NationalChip grus SDK material already authenticated
by `analyze_g2_codec_fwpk_segments.py`. The stage-two placement and KWS split
are authenticated by `analyze_g2_codec_stage2_sections.py`. This ledger
composes those analyzers; it does not claim that public format code is the
exact source of the official C-SKY bodies or trained model.

The official blob is an Even/NationalChip-derived binary. No redistribution
grant is recorded. Nothing in this increment relicenses that binary, the
gxNPU command stream, initialized data, or model weights.

## Classification delta

Before these boundaries, the 326,000 non-metadata bytes were 11 proprietary-
unavailable spans. The cumulative classification moves all 11 non-metadata
spans / 326,000 bytes to the typed-external category and leaves zero bytes
unclassified. Source-owned and blocking-byte totals do not change.

## Verification

```sh
python3 g2/tools/analyze_gx8002_source_readiness.py --json
python3 -m unittest g2.tests.test_gx8002_source_readiness
python3 -m unittest \
  g2.tests.test_analyze_g2_codec_fwpk_segments \
  g2.tests.test_analyze_g2_codec_stage2_sections \
  g2.tests.test_analyze_g2_drv_gx8002b
```

The focused tests execute the boundary against the locally authenticated
official model, reject and clear mutated or truncated model output, verify
the missing-provider path, build import-free host and Cortex-M55 objects,
and exercise analyzer drift failures. These are software-only checks.

Hardware qualification is **blocked by unavailable physical evidence**. Future release
acceptance still requires physical validation of model staging/inference,
runtime XIP/SRAM mapping, and dual-firmware selection, but those checks do
not block this software-only readiness classification.

## Remaining opaque frontier

There is no remaining unclassified byte span. The final gxNPU KWS command
stream (9,164 bytes) and initialized runtime-data spans (2,928 and 2,196 bytes)
now have exact typed provider boundaries. This is classification closure, not
source completion: all 326,000 non-metadata bytes still require external
authorized payload providers. Exact source admission requires an
authenticated NationalChip/Even source checkout whose generated C-SKY bytes,
ABI, configuration, and license close against the official spans. Until
then, they remain proprietary-unavailable with no production route.
