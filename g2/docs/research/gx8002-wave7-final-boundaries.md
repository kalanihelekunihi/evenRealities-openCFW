# GX8002 final command/data boundary classification

Status: Wave 7 assigns exact typed external provider seams to every remaining
unclassified byte. The exhaustive 326,092-byte package now contains 92 bytes
of reconstructible format metadata and 326,000 bytes of typed external
payload. Source ownership remains zero and every non-metadata byte remains a
blocking external dependency.

## Final spans

| Span | Package extent | Bytes | Authenticated evidence |
|---|---|---:|---|
| gxNPU KWS command stream | `[0x18D90,0x1B15C)` | 9,164 | segment `[0xF804,0x11BD0)`, exact size getter, decoded DRAM staging `0x20003304`, SHA `c38ed6d2…1430b9` |
| image-B initialized data | `[0x4EE5C,0x4F9CC)` | 2,928 | segment `[0x458D0,0x46440)`, derived text/data split but exact authenticated bytes, SHA `4b694344…13f884` |
| image-A initialized data | `[0x184FC,0x18D90)` | 2,196 | segment `[0xEF70,0xF804)`, authenticated text tail/fill/data head and exact fit, SHA `e0a88003…034384` |

The gxNPU command format is proprietary and unresolved. A size getter and
staging address do not reconstruct command semantics. Likewise, initialized
data bytes are not equivalent to source declarations. No semantic source is
claimed for any final span.

## Boundary behavior and ownership

The three wrappers are original MIT code over the reviewed exact-segment
SHA-256 verifier. They embed no command or initialized-data bytes. Missing,
failed, truncated, or identity-mismatched providers fail closed and clear the
destination.

Every payload remains `NOASSERTION` for source license and unresolved for
binary redistribution authority. No production route exists. Any provider
must independently establish lawful acquisition and redistribution.

## Final accounting delta

| Category | Before | After | Delta |
|---|---:|---:|---:|
| Typed external | 311,712 B / 8 spans | 326,000 B / 11 spans | +14,288 B / +3 |
| Proprietary unavailable/unclassified | 14,288 B / 3 spans | 0 B / 0 spans | −14,288 B / −3 |
| Reconstructible format metadata | 92 B / 6 spans | 92 B / 6 spans | 0 |
| Source-owned | 0 B | 0 B | 0 |
| Blocking external content | 326,000 B | 326,000 B | 0 |

Thus opacity classification is exhaustive, but community source feasibility
still requires lawful providers or authenticated distributable source for all
11 typed spans.

## Verification

```sh
python3 g2/tools/analyze_gx8002_source_readiness.py --json
python3 -m unittest \
  g2.tests.test_gx8002_source_readiness \
  g2.tests.test_gx8002_wave7_final_boundaries \
  g2.tests.test_analyze_g2_codec_stage2_sections
```

The software-only suite covers all final spans, mutation, truncation, provider
failure, destination clearing, host/Cortex-M55 import graphs, exhaustive
partitioning, and parent evidence. No hardware action occurs.

Hardware qualification remains **blocked by unavailable physical evidence**. Future
acceptance retains physical command execution, memory mapping, and inference
checks without weakening the current fail-closed software boundary.
