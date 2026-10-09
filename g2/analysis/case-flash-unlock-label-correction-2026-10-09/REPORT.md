# Case FLASH unlock label correction

Static instruction/literal and pinned HAL-source comparison PASS. Historical symbols are preserved unchanged. Corrected associations:

| Original address range | Historical label | Supported association |
| --- | --- | --- |
| 0x08004B6C–0x08004B88 | HAL_FLASH_Unlock | HAL_FLASH_OB_Unlock |
| 0x08004BF4–0x08004C10 | HAL_FLASH_OB_Unlock | HAL_FLASH_Unlock |

Both28-byte slices decode into14Thumb instructions; six PC-relative literal reads were independently resolved using aligned(address+4)+offset. Both base literals are FLASH0x40022000. First uses CR+0x14, shift-left1/sign test (bit30), writes+0x0C with observed keys0x08192A3B/0x4C5D6E7F. Second uses sign of CR (bit31), writes+0x08 with observed keys0x45670123/0xCDEF89AB. Existing CMSIS device header identifies OPTLOCK30, LOCK31 and OPTKEYR+0x0C/KEYR+0x08. Header/input hashes and complete addressed listings are retained. Observed key constants are byte evidence; this packet does not claim newly authenticated producing HAL-header key macro definitions.

Pinned official HALa0cf8a8b96183fdcc2e3b1cf0bcf0825f27bd0c9 source matches the opposite-name status/control semantics: option unlock defaultsHAL_ERROR1 and returns0 only after an initially locked bit clears; ordinary unlock defaultsHAL_OK0 and returns1 only if initially locked bit stays set. Already-unlocked option returns1, ordinary returns0. This discriminator, bit identity and destination independently support reversal, not merely key-name intuition.

No MMIO/device execution occurred. Readable pseudocode records two separate CR reads and ordered key writes; it does not force a lock bit to clear. These56codebytes are a corrected association of historical extents, not new source-produced bytes or whole-HAL release attribution. A genuine byte-producing comparator needs authenticated HAL/device/configuration headers and producing armclang/armlink version/configuration. No source substitutions/flag sweep were used. Historical Strong labels remain pending canonical owner's independently reviewed correction.
