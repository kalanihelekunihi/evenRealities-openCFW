# IAR runtime memory-provider source candidate

Scope: official G2 `2.2.6.10` Apollo-main `__aeabi_memcpy` and
`__aeabi_memmove` providers. Status: production-integrated and reproducible in
both reviewed toolchain profiles.

## Result

The clean-room Thumb-2 module
[`iar_runtime_memory.S`](../../components/apollo_main/core_overlay/candidates/iar_runtime_memory.S)
provides three independently extractable void-EABI entries:

| Candidate entry | Target bytes | SHA-256 | Relocations |
|---|---:|---|---:|
| `open_cfw_iar_memcpy_void` | 152 | `ee2582dc5c82d4bd438403a2682be0debc10c301ec0549942b7c56baa61d026f` | 0 |
| `open_cfw_iar_memcpy_aligned_void` | 152 | `ee2582dc5c82d4bd438403a2682be0debc10c301ec0549942b7c56baa61d026f` | 0 |
| `open_cfw_iar_memmove_void` | 322 | `2dbb1c506a291cc94fc624d492c0b55cd09e011e317bb21fd31004ee40a965b5` | 0 |

The selector-isolated source file is 6,903 bytes with SHA-256
`3afa1466d5bd4d57a81d6b31debbb077eee1cecab029eebfbeff690a7658841d`.
It preserves the stock void calling contract and handles zero counts. The
16-byte burst paths save and restore `r4`/`r5`, use caller-saved `r3`/`r12`,
and perform word loads only after aligning the source. Aligned destinations use
word stores; halfword-aligned and odd destinations use stock-shaped scatter
stores. The separate aligned entry is mandatory
because 597 stock calls target the IAR provider's interior entry `0x00439C04`
directly.

`memmove` copies forward when `destination <= source` or the regions do not
overlap, and backward for `source < destination < source + count`. Its
overlap test uses an overflow-safe pointer difference. Arbitrarily aligned
regions fall back to byte operations; equally aligned regions use byte
alignment prologues, 16-byte bursts, and word/byte tails. None of the three entries is presented as
ISO C `memcpy`/`memmove`, because the official routines advance `r0` and the
authenticated callers do not consume a destination return value.

## Qualification

The Apple clang 21.0.0 Cortex-M55 build produced one section per entry with
two-byte alignment, no text/data relocation, and no dependency. Static pins
are enforced by
[`test_iar_runtime_memory_candidate.py`](../../tests/test_iar_runtime_memory_candidate.py).

Lorelei then executed the exact three extracted binary sections with Unicorn
2.1.4. Each entry passed 2,000 deterministic vectors (6,000 total), including:

- every length from zero through 19;
- 31/32/33, 63/64/65, 127, 255/256, and 511-byte boundaries;
- randomized lengths through 767 bytes;
- every source/destination byte alignment combination; and
- forward, backward, identical, partially overlapping, and non-overlapping
  `memmove` regions with full-buffer guard comparison.

The tracked emulator is
[`emulate_g2_iar_memory.py`](../../tools/emulate_g2_iar_memory.py), SHA-256
`7bb4aba965f3429f01c16aad38e4132b95dab8026d1e2059fa5208b522e2dc91`.
The disposable remote qualification directory is
`/var/tmp/opencfw-iar-memory-qualify-20260808`; exact target hashes above, not
that path, are the evidence identity.

## Instruction-count optimization

The first semantically correct four-byte-loop candidate was rejected as a
performance regression: at 1,024 aligned bytes it executed about 5.7--5.8
times as many Thumb instructions as stock. The current 16-byte burst revision
was then requalified semantically and compared with the authenticated stock
island on Lorelei:

| 1,024-byte case | Stock instructions | Candidate instructions | Ratio |
|---|---:|---:|---:|
| public memcpy, aligned | 273 | 272 | 0.9963 |
| public memcpy, same unaligned (`1,1`) | 293 | 308 | 1.0512 |
| public memcpy, mismatched (`1,2`) | 2,075 | 2,080 | 1.0024 |
| aligned memcpy entry | 267 | 272 | 1.0187 |
| memmove, forward non-overlap | 278 | 279 | 1.0036 |
| memmove, backward aligned overlap | 279 | 279 | 1.000 |
| memmove, backward mismatched | 2,068 | 2,070 | 1.0010 |

This is Unicorn executed-instruction count, not a Cortex-M55 cycle benchmark.
It proves that both aligned and mismatched-alignment paths are within about 5.2%
of stock in this proxy, with most cases within about 2%. The tracked comparison tool is
[`benchmark_g2_iar_memory.py`](../../tools/benchmark_g2_iar_memory.py),
SHA-256 `df0b0fd1fb416930c5a3f5ec960391bd2fe9fd293e7bad5f9a1a2b7738c25aa4`.
The complete 9,951-byte JSON result has SHA-256
`73f34e06fb2cdfda6b30855ade72c9052bf21c200a9a2305444421f9d57622dd`.

## Production integration

All production gates are closed. Three append-only source leaves occupy
`[0x007B4030,0x007B42A2)` in the canonical component: memcpy at
`[0x007B4030,0x007B40C8)`, aligned memcpy at
`[0x007B40C8,0x007B4160)`, and memmove at
`[0x007B4160,0x007B42A2)`. The stock ownership is split into disjoint guarded
redirects at `[0x00439710,0x004397A6)`,
`[0x00439BE4,0x00439C04)`, and `[0x00439C04,0x00439C8A)`.

The canonical Apple-clang artifacts are overlay `130942` /
`ab8d461365df9a754ac608e69aceba0272541f568f3169332f8dc13536780eec`,
component `3654338` /
`b13dea2f77c48f37b309b7db55fb736f77abc24c217c56b20d96f7bb98d8a8bb`,
and package `4432832` /
`dbd7327ff42d80c8ff3b728ff9843f3a2b6e9bde3786bd68b929588d677539d5`.
Lorelei independently recorded and twice replayed the Linux-clang profile at
overlay `132810` /
`a1688164160c60f7bf1f1cbe326735d0ac4b2d260fff2b4fc13a9b662ec65e4a`,
component `3656206` /
`db3174b12d0a269c8e4c71304147f4122319e719e6bc1a66d1713a8ba91ac11e`,
and package `4434700` /
`03ec13df126c98f679e6e85c79cefea447943e746e74c8652e57ff71785ce2bf`.

The promotion adds 626 source bytes and reclassifies 316 stock bytes from
opaque to generated redirect ownership. No device was flashed or executed;
hardware timing remains a late-stage verification item.

## Reproduction

```sh
python3 -m unittest -v tests.test_iar_runtime_memory_candidate

# On a host with Python Unicorn, after extracting the three pinned sections:
python3 tools/emulate_g2_iar_memory.py /path/to/extracted-sections --iterations 2000
python3 tools/benchmark_g2_iar_memory.py /path/to/extracted-sections /path/to/stock-island --json
```
