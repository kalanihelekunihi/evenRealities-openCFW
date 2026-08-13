# Goodix GH_HRV provider boundary

## Decision

The nine-function / 1,288-byte lifecycle around `GH_HRV_pre_pv_v1.0.1.0_ed953ff3` is
Goodix GH3X2X provider code. Seven formerly unclassified functions / 1,154 bytes are now routed to
`goodix_gh3x2x_candidate` with disposition `vendor_source_required_not_redistributable`; the
output wrapper and version builder were already gated. OpenR1 does not recreate any of these
functions and requires a licensed provider for HRV preprocessing.

| Entry | Bytes | Boundary role |
| --- | ---: | --- |
| `0x0002CAC6` | 18 | cleanup dispatcher wrapper |
| `0x0002CC5C` | 46 | output dispatcher wrapper |
| `0x0006DA9C` | 4 | configuration getter |
| `0x0006DAA4` | 30 | private ABI-version copier |
| `0x0006DAD0` | 126 | lifecycle cleanup |
| `0x0006DB58` | 4 | cleanup thunk |
| `0x0006DB5C` | 926 | lifecycle initializer |
| `0x0006DF14` | 76 | output wrapper |
| `0x0006DF60` | 58 | exact version builder |

## Exact identity and topology

The initializer at `0x0006DB5C` rejects null configuration, any size other than 24 bytes, and any
ABI string other than `pv_v1.1.0`. Its sole direct caller is `0x0006DF14` at `0x0006DF58`. That
wrapper constructs the exact `GH_HRV_pre_pv_v1.0.1.0_ed953ff3` identity, obtains the provider
configuration object, copies the same private ABI tag, and invokes the initializer. The Goodix
dispatcher wrapper at `0x0002CC5C` calls it at `0x0002CC68`.

The cleanup route is likewise closed: dispatcher wrapper `0x0002CAC6` calls thunk `0x0006DB58`
at `0x0002CACC`, which branches to `0x0006DAD0`. The version builder is also called from the
already gated Goodix algorithm-version dispatcher at `0x0002A14C`. These edges, every complete
body, and all identity strings are SHA-256 pinned.

## Recovered behavior, not admitted source

The 926-byte initializer allocates a 308-byte provider context plus 48-byte and 696-byte private
work areas through the separately gated sensor-algorithm heap. It chooses internal window and
buffer dimensions from sample counts in the 25/50/100/200 families, initializes eleven private
arrays, and converts four signed calibration values to provider floats. Cleanup releases those
arrays and work areas.

Those details establish ownership and the provider ABI boundary; they are not a specification for
a local substitute. The state layout, allocation scheme, buffer sizing, and calibration handling
belong to the proprietary HRV preprocessor. Product-owned downstream RMSSD/history behavior
remains separate from this boundary.

The static verifier can reproduce the census with:

```sh
python3 tools/evidence/summarize_r1_goodix_hrv_boundary.py
```
