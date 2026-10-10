# IAR scatter destination-mode discriminator

Date: 2026-10-10  
Scope: private P2/build-path evidence only  
Worker: Daybreak Blue Low

## Result

The complete authenticated Apollo-main scatter table at `0x0075D3C8..0x0075D410` contains five destination contracts, and every one selects the absolute-address form. None selects the `r9`/static-base-relative form supported by the exact IAR handlers.

The first table row selects exact IAR `__iar_zero_init3` at `0x005FA01E`. Its descriptor stream has two nonzero entries followed by the zero terminator:

| Length | Destination word | Mode |
| ---: | ---: | --- |
| `0x00070AF0` | `0x20004558` | absolute |
| `0x00240FD4` | `0x2013BE70` | absolute |

`__iar_zero_init3` tests destination-word bit 0 and uses `r9 + word - 1` only when that bit is set. Both stock destination words are even, so neither descriptor exercises that branch.

The remaining three rows select the exact in-image IAR decompressor at Thumb address `0x0043A11F`. For this handler, packed-length bit 0 selects static-base-relative destination addressing. All three packed-length words are even:

| Row | Packed length | Stored input bytes | Destination | Mode |
| ---: | ---: | ---: | ---: | --- |
| `0x0075D3E0` | `0x0000002C` | 22 | `0x00000040` | absolute |
| `0x0075D3F0` | `0x000054E0` | 10,864 | `0x20000000` | absolute |
| `0x0075D400` | `0x0000434E` | 8,615 | `0x20080000` | absolute |

The verification script authenticates the 3,523,364-byte headerless image as SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`, recomputes the runner's table bounds, walks the zero descriptor terminator, validates all three compressed-source spans are inside the image, and asserts the five mode bits. Replay with:

The three compressed inputs also form one gapless stored tail, in reverse row order: `[0x0078F6F7,0x0079189E)`, `[0x0079189E,0x0079430E)`, and `[0x0079430E,0x00794324)`. The final byte is the authenticated image's exclusive end. That ordering and packing boundary are additional exact linker-output constraints; they still do not identify the option spelling that produced them.

```sh
python3 g2/analysis/iar-scatter-destination-discriminator-20261010-daybreak/verify.py
```

## Build-path implication

This original-byte contract narrows the startup image: its emitted scatter records use absolute destinations only. A byte-identical reconstruction must reproduce these five unflagged contracts, their order, handler selection, and exact table extent. A candidate linker configuration that emits static-base-relative flags for any of these records is excluded.

This does **not** identify a unique IAR library archive, compiler release, ICF, linker option set, or whole-program data model. In particular, handler support for `r9` relocation is a runtime capability and is not evidence that the stock application selected RWPI. Conversely, absence of flagged records in this complete scatter table does not prove no code elsewhere uses `r9` or exclude every RWPI-related compiler option. It establishes the producing table's destination mode, not the producing project's complete configuration.

## Exhaustion boundary

The initializer-table branch exposed by the ten-body IAR review is now closed at the available byte-contract level. The complete table was already bounded by the stock runner, and all five destination-mode selectors are accounted for. Re-scanning these rows or comparing additional copies of the identical runtime handlers cannot further distinguish the producing configuration.

Further discrimination requires a producing `.ewp`/ICF/linker map or option receipt, an IAR output from a controlled configuration matrix that reproduces the entire table bytes and placements, or another authenticated stock construct whose encoding changes across candidate configurations. This report changes no firmware source, canonical ledger, gate receipt, submodule, or authenticated input. The campaign remains `P2_EXECUTING`; G2 through G6 remain closed.
