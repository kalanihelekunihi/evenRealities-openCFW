# G2 bootloader TLSF request-size and class-mapping source closure

## Result

The three complete authenticated entries at `[0x00416BCE,0x00416C4E)` now route to compilable freestanding C in `components/bootloader/core_overlay/runtime_tlsf_mapping_416bce.c`. The 3,464-byte source file has SHA-256 `4c7c107d4e9d1d2cf06e5a80fb497ed17195adeb9a9a3b4052fae42b8ddee2f2` and is a bounded BSD-3-Clause adaptation of Matthew Conte TLSF v3.1 for the recovered G2 ILP32 allocator configuration.

| Function | Stock span | Stock bytes | Direct callers | Compiled bytes | Strict relocations |
|---|---:|---:|---:|---:|---:|
| adjust request size | `[0x00416BCE,0x00416BF8)` | 42 | 1 | 30 | 1 |
| insert class mapping | `[0x00416BF8,0x00416C26)` | 46 | 3 | 42 | 1 |
| search class mapping | `[0x00416C26,0x00416C4E)` | 40 | 1 | 46 | 2 |

The tranche closes 128 authenticated stock bytes with 118 compiled bytes and four strict source-to-source relocations. It preserves zero-size rejection, four-byte alignment, the 12-byte minimum block, the exclusive `0x40000000` maximum, the 128-byte small-block threshold, 32 second-level classes, first/second-level insertion mapping, and allocation-search rounding to the containing class.

## Verification

`tests/test_runtime_bootloader_tlsf_mapping_416bce_416c4e.py` authenticates all three stock spans, checks request-size boundaries and mapping/rounding behavior, and requires a warning-clean Cortex-M55 freestanding compile. `tools/analyze_g2_bootloader_numeric.py` pins all callers, compiled bytes, relocations, exact redirects, both reviewed compiler profiles, provider ownership, and both complete unsigned packages.

The current aggregate is 106 routed functions and 64 runtime functions: 5,080 authenticated runtime stock bytes, 4,318 compiled runtime bytes, 234 direct callers, two registered-pointer ingress paths, and 111 strict relocations. Provider accounting is 5,423 source-owned bytes, 6,532 generated patch bytes, 12 alignment bytes, and 142,067 retained official bytes.

The Apple profile produces a 5,434-byte overlay (`4614a0b138d85cdf3334f6f0096ef2a40476857460355c0a69ea9fdaa164f893`), a 154,034-byte provider (`b86ee97297ae98a6fae2d371a6148aeb90dba9f6e15bcf456d56122ed1d4accd`), and a 4,735,612-byte unsigned package (`a0c1d990deaeab072b6e5e53bfdf2aec2f7c02a7ed76d39ca452af2cf9433954`). The Linux profile produces a 5,418-byte overlay (`b816f9668736c0407a71d301b529d6aa82e9324293f2e5f4bdf0caca3815a2da`), a 154,018-byte provider (`438ec01b58587c84ad04eba24987e42ad26ea76a812536c772d4741ddc766c6f`), and a 4,511,606-byte unsigned package (`a0c082dc520e4ce1a26f6c22ea6dcb90972ac6595c52aa037bda8ac6f2f07c72`).

## Remaining boundary and hardware evidence

The next complete callable body begins at `0x00416C4E`; `[0x00416C4E,0x00417AD4)` remains a 3,718-byte software gap before the already routed EasyLogger entries. No image was signed, flashed, installed, reset, or booted. Live allocator-class selection, fragmentation/coalescing, allocation caller paths, and boot validation remain explicitly blocked because no authorized responsive G2 right temple is available. This tranche is software-closed, but firmware-wide functional completeness is not claimed.
