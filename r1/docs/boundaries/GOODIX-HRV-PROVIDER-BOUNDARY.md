# Goodix GH_HRV provider boundary

## Decision

The nine-function / 1,288-byte lifecycle around `GH_HRV_pre_pv_v1.0.1.0_ed953ff3` is
Goodix GH3X2X provider code. Seven formerly unclassified functions / 1,154 bytes were routed to
`goodix_gh3x2x_candidate`; all nine entries are now transparent under the owner-authorized
reconstruction. The former `vendor_source_required_not_redistributable` disposition is retained
only as historical provenance; no function in this bounded lifecycle still requires opaque input.

| Entry | Bytes | Boundary role |
| --- | ---: | --- |
| `0x0002CAC6` | 18 | cleanup dispatcher wrapper |
| `0x0002CC5C` | 46 | source-admitted initialization dispatcher wrapper |
| `0x0006DA9C` | 4 | configuration getter; source-admitted as explicit binding |
| `0x0006DAA4` | 30 | private ABI-version copier |
| `0x0006DAD0` | 126 | lifecycle cleanup; source-admitted typed destructor |
| `0x0006DB58` | 4 | cleanup thunk; maps to the same destructor |
| `0x0006DB5C` | 926 | source-admitted complete lifecycle initializer |
| `0x0006DF14` | 76 | source-admitted sample-count/configuration wrapper |
| `0x0006DF60` | 58 | exact version builder; source-admitted bounded text |

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

## Cleanup closure

The cleanup body calls the already reconstructed release-and-clear primitive
for eleven owned subobjects in exact stock order at context offsets `0x94`,
`0xA8`, `0xB8`, `0xC8`, `0x1C`, `0x2C`, `0x3C`, `0x4C`, `0x5C`, `0x74`, and
`0x84`, then releases the allocations at `0x6C` and `0x70`, releases the
enclosing context, and clears the global owner. The transparent typed form
preserves that 14-release ownership graph while adding null-safe idempotence.
Tests pin release count, owner clearing, and repeated teardown.

The version builder is also fully local: it emits the exact 31-byte identity
`GH_HRV_pre_pv_v1.0.1.0_ed953ff3` plus NUL into a checked 32-byte-or-larger
destination. The test pins the complete string and short-buffer rejection.

## Initializer and wrapper closure

The 926-byte initializer is now typed C. It preserves exact status values
`0x10000001`, `0x10000002`, and `0x10000004`; the 24-byte configuration and
`pv_v1.1.0` ABI gate; the four 25/50/100/200 sample-count geometry families;
all eleven float-buffer capacities; 48-byte and 696-byte work records; and
the recovered calibration order divided by `10000.0f`. The reconstruction
also rolls back every successful allocation on failure instead of retaining
stock's partial context.

The `0x0006DF14` wrapper copies the explicit caller-supplied configuration,
overrides its sample count, and invokes that initializer. The `0x0002CC5C`
dispatcher makes its former globals explicit, writes result status `0x7F`
only on success, and clears both activity bindings on every provider result.
Tests cover every geometry family, the default geometry, exact capacities and
work-record fields, calibration ordering, already-initialized rejection,
partial-allocation rollback, wrapper override, dispatcher results, and full
teardown. Product-owned downstream RMSSD/history behavior remains separate
from this now-closed preprocessing lifecycle.

The static verifier can reproduce the census with:

```sh
python3 tools/evidence/summarize_r1_goodix_hrv_boundary.py
```
