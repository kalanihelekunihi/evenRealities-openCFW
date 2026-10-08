# GX8002 KWS model extent verifier

Run from any directory with:

```sh
python3 g2/analysis/rescan-2026-10-07/implemented/gx8002/verify_model.py
python3 g2/analysis/rescan-2026-10-07/implemented/gx8002/test_wrong_extents.py
```

The verifier reads only the locked `g2-2.2.6.10` `firmware_codec.bin`. It pins
the payload size and SHA-256, validates the actual stock instruction bytes for
all five `LvpModelGet*Size` getters, validates the stock task-initializer body,
and recomputes command/weight boundaries and hashes from image A. Its output is
metadata only: no command or weight bytes are copied or written. `--output`
can save the JSON metadata result.

The compiled getter values are command 9,164 bytes, weight 120,800, ops 0,
data 13,056, and temporary memory 4. The stock task routine's raw body hash is
also checked. The GRUS layout corroboration comes from NationalChip LVP pin
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5` and the independently reviewed
consumer mapping; use the GRUS task (`cmd` at `+0x14`, `weight` at `+0x1c`),
not the LEO variant. Component licensing varies. This tool copies no vendor
headers or model source.

For the locked codec image, image A's command extent is `[0xF804,0x11BD0)` and
weights are `[0x11BD0,0x2F3B0)`. The stock KWS staging evidence supports
conditional CPU-visible destinations `0x20003304` and `0x200056D0`; its separate
review explicitly leaves XIP/runtime mapping, successful reads, NPU execution,
and accelerator semantics unresolved. The command stream is executable by the
NPU; weights are model data. Neither is ordinary MCU code. This is model-region
interface metadata and an extent check, not a claim of source completeness,
trained-model provenance, or a byte-identical firmware rebuild.

Evidence already bound to the locked image:

- `g2/tools/analyze_g2_codec_stage2_sections.py` independently checks the
  getter literals, `0xF804` load-offset literal, and exact fit at the image-B
  boundary.
- `g2/build/pseudocode-first/20260930T190500Z/reviews/codec-npu-staging-review-053/review.json`
  checks source spans and conditionally supports the staging tuple.
- `g2/build/pseudocode-first/20260930T190500Z/attempts/P1-codec-npu-consumer-mapping-061/001/consumer-proposal.json`
  records the task pointer-field translation and GRUS layout corroboration.

The test suite exercises the locked correct extent and rejects four altered
starts/lengths (command start/size and weight start/size).
