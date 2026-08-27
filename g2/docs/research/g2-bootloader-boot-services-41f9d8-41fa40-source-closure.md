# G2 bootloader delay and initializer-service source closure

The four complete bootloader service entries at
`[0x0041F9D8,0x0041FA40)` are now replaced by maintained clean-room C. They
provide the millisecond and raw delay wrappers, initializer-record priority
comparison, and the bounded boot-initializer runner. No upstream identity is
claimed.

## Authenticated stock and ingress bounds

| Entry | Bytes | SHA-256 | Authenticated ingress |
|---|---:|---|---|
| millisecond delay `[0x0041F9D8,0x0041F9E6)` | 14 | `f9d267ca0fe9273e71065d8d35b31cf4d296067d79e9787d7635113ae2ab6676` | five direct callers: `0x0041B866`, `0x004204AE`, `0x00420560`, `0x00420598`, `0x004304CE` |
| raw delay `[0x0041F9E6,0x0041F9EE)` | 8 | `dddd4579356bb2192ab70e96b40e55aed4767132acd66a48667053c1045ec591` | thirteen direct callers, including the source transport wait at `0x0041F98A` |
| priority comparator `[0x0041F9F0,0x0041F9F8)` | 8 | `c4fc4b65a098dcd475fdd6b5d696b5e7e3957c2af7e722653ea39798d642e3ad` | stored Thumb pointer `0x0041F9F1` at `0x0041FA4C` |
| initializer runner `[0x0041F9F8,0x0041FA40)` | 72 | `bc69f5a1adfd743601ee6cfc46e0397fa7ab4dfd46176d3d4b626f8361cccf22` | direct caller `0x0041B86A` |

The preceding `[0x0041F9B6,0x0041F9D8)` vector/literal island and the
two-byte `[0x0041F9EE,0x0041F9F0)` alignment gap remain authenticated
official non-executable bytes. The caller oracle scans every aligned Thumb
`BL`, and separately authenticates the stored odd comparator pointer.

## Recovered contract

`runtime_boot_services_41f9d8.c` is 6,978 bytes, SHA-256
`99aa433811660dd98b1e927d99fdbdb3d2214ad7a88d30ed36803305873cf693`,
under GPL-3.0-or-later. It preserves the complete observable contract:

- the millisecond wrapper performs wrapping 32-bit multiplication by 1,000
  before entering raw delay seam `0x0041D1C1`;
- the raw wrapper forwards its argument unchanged to the same delay seam;
- the comparator subtracts the unsigned priority words at record offset
  `+4` and returns the wrapped result through the stock signed 32-bit ABI;
- the runner copies eight-byte records from `[0x00433440,0x00433460)` to
  scratch `0x20022E00`, caps the record count at 256, and sorts through seam
  `0x00423D09` using stored Thumb pointer `0x0041F9F1`;
- it then invokes each non-null callback in sorted order and skips null
  callback records.

The authenticated image contains four initializer records:
`{0x004301D7,1}`, `{0x0043194D,1}`, `{0x00415591,25}`, and
`{0x0041FD71,26}`. Host tests cover delay forwarding and overflow, comparator
ordering, stable sorted dispatch, null skipping, a zero-length table, and the
256-record cap. A freestanding Cortex-M55 compile gate rejects warnings and
language-runtime dependencies.

## Dual-profile production evidence

Both reviewed toolchains emit relocation-free leaves:

| Leaf | Apple / Linux overlay offset | Bytes | SHA-256 |
|---|---:|---:|---|
| millisecond delay | `9224 / 9208` | 16 | `44ebf4e1f372017ceaa6885948b4e02f8dc5ede3c18f547a9d8e1a54e9db33f5` |
| raw delay | `9240 / 9224` | 8 | `071c3652bfd2017f385f368863d1ad8fa69b4f2bf93706786dbfc9899cad09dd` |
| priority comparator | `9248 / 9232` | 8 | `daa15c77ff9790a201193ce3e4a9cc74b8caf26827306a324f0889f4ed934ead` |
| initializer runner | `9256 / 9240` | 64 | Apple `7b81438b36f613dbd31af78de972c28814c93a8e4551f261c7b928bf944f4729`; Linux `3f8b87c0e6333223873a9e403787881fc7c23862ce9c5fc4bdaae1e4565e6776` |

Apple produces a 9,320-byte overlay ending at `0x004368E0`, SHA-256
`aaefcef3e31df12ec06a2ee7f505430f17daba8061099677143b24505ea96dc7`,
and a 157,920-byte provider, SHA-256
`56350fb0fc8d663dc2202f11389573b52ddd30536e81f44539006f7810f2744d`.
Linux produces 9,304 / 157,904 bytes with SHA-256
`6be4f564d6ef9ace9c98de17bf2cc082142440a3da3716521a9e3e529ebb017b`
and `3961d3432af2cbeb83731d79792071161980decbc6cf635c57b6a396f09f3504`.
Canonical accounting is 9,307 source-owned, 10,644 generated patch, 14
alignment, and 137,955 retained official bytes across 155 functions, 136
relocated leaves, and 153 patch sites. Apple retains 5,920 bytes of overlay
headroom.

The unsigned Apple package is 4,739,498 bytes, SHA-256
`115c5ad73e32e308287034d1b1120f8ed576ec3c3c9294cafce1bfc561b727f9`.
Its 4,490,259-byte flash plan hashes to
`963c0cc5459a9d2ddbf522ab0b47cb03683f850334c910c9c68c92070d0a3c01`
and records 6,456 placed, two unresolved, five container-only, and six
protected regions. The Linux package is 4,515,492 bytes, SHA-256
`e742a5b7775cf8aae0667e0a425a76a83c9032406a28bcd679bfb82529de8c92`;
its 2,391,096-byte plan hashes to
`f390315a15b17c7b4bece666f9019b7006228a8a3e5ae22d41f879ff85186aaa`
and records 3,427 placed regions with the same unresolved/container/protected
boundaries.

No signer, device, debugger, UART, transport, flasher, reset, or boot path was
accessed. Live clock accuracy, scheduler interaction, initializer ordering,
callback side effects, and cold-boot evidence remain blocked: there is no
authorized responsive right G2 temple, and the authorized left temple must
remain stock. Later retained executable bootloader bodies remain software
gaps, so firmware-wide functional completeness is not claimed.
