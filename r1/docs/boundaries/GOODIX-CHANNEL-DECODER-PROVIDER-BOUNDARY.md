# Goodix packed-channel decoder provider boundary

## Decision

Two formerly unclassified functions / 856 executable bytes are routed to
`goodix_gh3x2x_candidate` with disposition `vendor_source_required_not_redistributable`. They are
private packed-channel decoding and floating-point scaling code, not R1 product behavior, and are
not eligible for local reconstruction.

## Exact closure

| Entry | Bytes | SHA-256 | Role |
| --- | ---: | --- | --- |
| `0x000335B4` | 522 | `f9972cff9f72e10bd9b1bfb21ebaaa92763a058f8f857ef46bd5f1b7c61e0e3f` | private packed-channel scaling helper |
| `0x00061DA4` | 334 | `39fff2899dacfbad91bcff003cedfdac2ce2d9f0fbdd26f7f01db54927a98bfe` | three-channel presence-mask decoder and output-record assembler |

The decoder's sole direct callsite is `0x0006E874`, inside the already SHA-pinned Goodix GH3X2X
provider component. It calls the previously gated Goodix shared-version qualifier at
`0x00066890`. Its three scaling-helper calls are exactly `0x00061E42`, `0x00061E86`, and
`0x00061ECA`; the helper has no outside caller.

The decoder walks three channel groups under a packed presence mask and assembles fixed output
records. The helper selects private width/mode tables and applies floating-point scaling and
coefficient formulas. Those semantics and the closed provider-internal callgraph establish the
vendor boundary; they do not authorize copying the private lookup tables, constants, formulas,
or inferred implementation.

## Provider rule

Use a lawfully obtained Goodix GH3X2X provider package with recorded version, hashes, ABI,
license, and redistribution terms. Until then:

- do not recreate the channel decoder, scaling formulas, or coefficient tables;
- do not infer private symbols from the descriptive boundary labels;
- retain Arm floating-point/toolchain helpers as separately source-routed dependencies; and
- keep live optical processing disabled.

The summarizer is static, reads no live sensor data, and emits no private coefficients or
algorithm implementation.

## Reproduce

```sh
python3 tools/evidence/summarize_r1_goodix_channel_decoder.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
