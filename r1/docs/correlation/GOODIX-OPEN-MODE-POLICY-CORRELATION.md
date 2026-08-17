# Goodix open-mode policy correlation

The R1 optical open-mode callback at `0x0008165C..<0x0008170A` is a 174-byte
function with SHA-256
`eecd6ba14ea56d621ef0731e0c3e7166b68eba67bee08576c5635a37531e0b0e`.
Ghidra omitted the entry because it lies inside unrelated noncontiguous function
bounds, so the exact body is a manual provenance supplement.

The callback has no direct branch callers. Its Thumb pointer `0x0008165D` is
stored at `0x0009A59C`. The ten-byte `TBB` table at `0x000816B0` routes narrowed
mode values `0...9`; every nonzero original input eventually tail-branches at
`0x000816F4` to the already separated optical provider adapter `0x00050B00`.

The product-owned action before that provider boundary is a bounded state-clear
plan over the 240-byte optical backing state:

| Open mode | Clear offset | Clear bytes | Registered topic |
| --- | ---: | ---: | --- |
| `1` | `0` | `16` | `hr` |
| `2` | `40` | `24` | `hrv` region |
| `3` | `188` | `2` | `wear` |
| `4` | `16` | `24` | `spo2` region |
| `5` | `64` | `124` | `raw_hr` |
| `6` | none | none | unlabeled; shares mode 2's provider path |
| `7` | `216` | `24` | `adt` |
| `8` | `192` | `12` | `gray` |
| `9` | `204` | `12` | `aging` |

An original zero input returns without opening the provider. Nonzero inputs are
narrowed to `uint8_t`, and even modes outside `0...9` are forwarded without a
state clear. The `ppg open type:%d` diagnostic is selected only when the
narrowed mode is at most four.

`r1_goodix_open_mode_plan_build` exposes this mapping without clearing live
memory, invoking Goodix, logging, or providing a public optical-control route.
Those effects remain explicit composition boundaries.

Reproduce the exact extent/hash, callback pointer, `TBB` targets, state base,
diagnostic, and provider tail-call checks with:

```sh
python3 tools/evidence/summarize_r1_goodix_open_mode_policy.py
```
