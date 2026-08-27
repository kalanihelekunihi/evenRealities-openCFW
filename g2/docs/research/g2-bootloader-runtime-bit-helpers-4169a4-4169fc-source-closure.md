# G2 bootloader bit-helper source closure

Status date: 2026-08-26  
Target: official G2 `s200_v2.2.6.10` Apollo bootloader

## Authenticated entries

Three adjacent complete entries are source-owned:

| Stock span | Bytes | SHA-256 | Direct callers | Contract |
| --- | ---: | --- | --- | --- |
| `[0x004169A4,0x004169E2)` | 62 | `a3a7efceaf507b98b5ba00ead31f0713ef289324a180c1d017b50db781d57d0f` | `0x004169EA`, `0x004169F4` | unsigned 32-bit bit width (`0` for zero) |
| `[0x004169E2,0x004169F2)` | 16 | `32c3e2591f32bbda0aae71b2b2f742e3dd76405163ed9f53a40086a51d8119ef` | `0x00416C86`, `0x00416CB0` | trailing-zero count via isolated low bit |
| `[0x004169F2,0x004169FC)` | 10 | `da2cf0f5cd806a2ec1fddd96dbf2770c4421098b26bc3380c539d5b83428d126` | `0x00416C10`, `0x00416C36` | unsigned floor-log2 |

The two adapters preserve the stock zero-input wraparound result
`0xFFFFFFFF`; the source does not invoke undefined compiler builtins. No
stored entry pointer or strict-interior ingress was found. The next complete
body starts at `0x004169FC`.

## Source/build closure

The three GPL-3.0-or-later clean-room sources are
`runtime_bit_width_4169a4.c`, `runtime_ctz_4169e2.c`, and
`runtime_log2_4169f2.c`. Apple clang 21 and Homebrew clang 22.1.8 both emit
14, 14, and 10 bytes. Bit width is relocation-free; each adapter has one
strict call relocation to the source-owned bit-width helper. Hosted tests
cover zero, every single-bit boundary, signed-bit patterns, all-ones, and 256
deterministic random inputs. Freestanding Cortex-M55 compilation, exact stock
spans/callers, generated redirects, mutation-set checks, both provider
profiles, and manifest ownership pass offline.

Canonical accounting is 4,927 source-owned bytes, 5,938 generated patch
bytes, 12 alignment bytes, and 142,661 retained official bytes. The
4,938-byte overlay hashes to
`0c9199959aa2fe7cfd7e7175456eaffaeed8714206bae0da4b37b6472cd35d89`;
the 153,538-byte provider hashes to
`6a5b099d8691df3203ac6137de7a1640ed53d6b7d1f070142c973ad4ae0dcd11`.
The canonical unsigned package is 4,735,116 bytes /
`7acbcd11e678f753121ae7e27e689611c4218780ea52fedb96ab5d2eef7068d9`;
the Linux package is 4,511,110 bytes /
`14bcef108647316d9ed1433a3b5765b118c02277a63b3c32e687d355d22bcccb`.

No signing, flashing, installation, reset, boot, or hardware operation was
performed. Live callers and any timing-sensitive behavior remain explicitly
blocked by unavailable authorized responsive G2 hardware. Firmware-wide
functional completeness is not declared.
