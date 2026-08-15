# 32...63-byte frontier correlation

The 32...63-byte inventory tier is now source-routed: 151 functions, 6,636 declared body
bytes (6,468 range-pinned; 168 remote continuation bytes recorded as omitted). Nineteen
functions in the tier stayed unclassified: mostly generic libc-like helpers reached from gated
scopes (excluded per the GoMore auth-parser boundary's no-transitive-admission precedent),
zero-caller utility bodies, the Nordic peer-manager guard wrapper `0x0005C034` (no exact SDK
match and no R1 markers), and the GXT310 scaled register read `0x0006F80C` (vendor/glue split
unresolved).

| Family | Functions |
| --- | ---: |
| R1 product-specific | 79 |
| Goodix GH3X2X candidate | 27 |
| GoMore licensed-provider candidate | 16 |
| Generic device-registry candidate | 13 |
| Shared quantized-neural runtime candidate | 9 |
| Sensor-stream framework candidate | 6 |
| Time/calendar provider candidate | 1 |

Every provider-candidate and unresolved-framework entry above carries the
`vendor_source_required_not_redistributable` or `investigate_before_implementing`
disposition and remains implementation-blocked.

Current reduction note: later owner-authorized work has source-admitted a
subset of these historical provider candidates. In this batch, `0x0002A65C`
became `goodix_primitives_send_fixed_aa_pair`: the global selector table and
provider-vtable address are explicit typed bindings, while the exact `AA AA`
payload, two-byte length, and caller-word forwarding remain local and tested.

## R1 kv.bin class accessor family

The 24-function cluster at `0x000735E0...0x00073968` and `0x0007BB94...0x0007CA44` is the R1
`kv.bin` class-accessor family. Scatter-decoded record headers at `0x20007DE8`, `0x20007DF0`,
and `0x20007DF8` exactly reproduce the seven KV class strides (dev_info 24+52, ble_mult 24+90,
health 24+12, hsync 24+24, power 24+4, nv_r1 24+124, r_size), and each wrapper's embedded length
field matches its class payload. This corroborates the implemented R1-owned four-snapshot class
store rather than adding new surface.

## Shared neural-runtime arena

`0x00091C48` and `0x0009371C` are mirror free/alloc over a 12-slot, 0x14-stride descriptor table,
matching the twelve-descriptor tensor-arena compactor/allocator pinned at `0x00093628`. They join
`unknown_shared_quantized_neural_runtime_candidate` pending an attributable source.

## Registry request-submit wrappers

The `0x00050F34`-shape wrappers fill a static request block and dispatch through the pinned
registry operation-table slots (0x10/0x14). The same body shape serves GXT310, IQS7211E, ST25DV,
and touch callers, so the family is framework ABI (`unknown_generic_device_registry_candidate`),
not device product code.

## Deliberate family splits

The intrusive list node alloc/link helper `0x0005D94A` is filed with the registry candidate
(consumed by the pinned registry insert `0x0005DB14`); parallel list consumers of the
sensor-stream framework remain blocked under that family. `0x0005A3D4` joins the shared
quantized runtime via its descriptor-runtime callee despite a GoMore-only caller; both readings
stay implementation-blocked either way. `0x0008AD08` composes two pinned time/calendar provider
bodies and joins that candidate family. `0x0005CB6C` and `0x0004E1E4` are R1 boot init-table
runners: the table at `0xC4534` contains pinned R1 adapter/registrar entries, and the
region/topology exclude a toolchain CRT interpretation.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_frontier_32_63.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
