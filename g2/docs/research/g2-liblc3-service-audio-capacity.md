# G2 LC3 service-audio whole-address capacity audit

The complete stock-ABI encoder route remains unplaced. This audit closes the
software-only size and address-space question without assigning bytes owned by
another provider or emitting an OTA image.

## Exact package model

`build/source/flash-plan.json` contains 5,995 nonoverlapping Apollo-main MRAM
regions that exactly cover `0x00438000..0x007ECA44` (3,885,636 runtime bytes).
The only unowned contiguous interval before the protected update record at
`0x007FE000` is the 71,100-byte append interval. The 12,828 generated PT
padding bytes and 4,332 alignment bytes, including the 2,434-byte LTPF rodata
cave tail, retain existing ownership and are not admitted for LC3 placement.

All six orders of the three indivisible LC3 XIP sections are enumerated. No
order fits. Moving only the 404-byte table into protected padding would still
leave an 8,752-byte Apple shortfall and therefore cannot justify taking that
ownership.

## Size experiment

The accepted `-Oz` plus section-GC closure keeps `LC3_PLUS_HR=0`, every
runtime-selectable non-HR configuration, all 11 external bindings, all five
read-only table objects, and complete final relocation replay:

| Profile | text | rodata | tables | relocations | linked-order shortfall | best-order shortfall |
|---|---:|---:|---:|---:|---:|---:|
| Apple Clang 21 | 19,360 | 60,480 | 404 | 485 | 9,156 | 9,152 |
| Homebrew Clang 22 | 19,308 | 60,480 | 404 | 486 | 9,108 | 9,100 |

Clang introduces a local `__aeabi_memcpy` helper at `-Oz`; the bounded
volatile-byte implementation keeps it inside the LC3 closure, so the external
binding set remains exactly 11. Host `-O2` and `-Oz` encoders produce identical
plans and output bytes over all admitted durations, rates, PCM formats, and the
reviewed bitrate grid.

Disabling section GC is rejected because it retains unexpected writable data.
LTO is rejected because it changes the authenticated 404-byte five-table
policy. `-fmerge-all-constants` produces zero section-size savings and is not
selected. These are fail-closed results, not optimization suggestions.

The already-audited 30,676-byte repack counterfactual would give the Apple
`-Oz` closure 21,532 bytes of margin, but that move is not implemented and does
not have production authority. Final runtime addresses, stock veneers, OTA CRC
regeneration, atomic package emission, and hardware qualification therefore
remain false.

A narrower follow-up now proves that the full repack is unnecessary. Moving
only the final 84 strict leaves (9,252 contiguous bytes) into seven
authenticated stock-slot NOP tails leaves the best-order Apple closure 96
bytes before the protected update record. The exact packing and all 288 suffix
relocations are authenticated in `g2-liblc3-service-audio-suffix-pack.md`.
Production routing remains false until the 11 runtime imports, final
485-relocation LC3 replay, and atomic OTA integration are authenticated.

Reproduce the result with:

```sh
python3 g2/tools/analyze_g2_liblc3_service_audio_capacity.py --pretty
python3 -m unittest -v \
  g2.tests.test_analyze_g2_liblc3_service_audio_capacity
```
