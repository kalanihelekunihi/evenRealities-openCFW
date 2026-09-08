# SPI-NOR device records

The six labels are now source-authored C strings in
runtime_gx8002_flash_device_names.c. Each has explicit byte alignment so the
compiled arrays fit the original tightly packed 52-byte interval, package
0x153e0..0x15414. Verification authenticates the firmware and pinned SDK
spi_nor_ids.o, checks the six independent object sections, and checks every
stock device record's name pointer and JEDEC ID. The SDK object is solely a
comparison oracle; neither strings nor object bytes are copied into the build.

| Label | JEDEC ID | Package name offset |
| --- | --- | --- |
| p25q21l | 854012 | 153e0 |
| p25q40l | 856013 | 153e8 |
| p25q80l | 856014 | 153f0 |
| en25s20a | 1c3812 | 153f8 |
| en25s40a | 1c3813 | 15401 |
| zb25wq80a | 5e3414 | 1540a |

The 168-byte record array at package 0x18638 remains retained: six 24-byte
records plus a zero terminator. Recovered discovery and information queries
establish name pointer (+0), JEDEC ID (+4) and usable byte count (+8).
Protection routines and the authenticated SDK relocations establish protection
profile pointer (+16); OTP routines and relocations establish OTP descriptor
pointer (+20). The word at +12 is 0x60 in the populated records and is still
unidentified. A familiar opcode value alone is insufficient to assign its
meaning or establish that it may safely be removed.

Pinned SDK spi_nor_ids.o has local BSS symbols protect_256k_type1,
protect_512k_type1 and protect_1m_type1, each eight bytes, and a 20-byte local
otp_type1 object. Its data relocations connect those objects to the same
respective device slots. It has no debug information section providing the
missing source struct field names. The reconstructed chip erase wrapper uses
range erase rather than reading the +12 word. No claim of unused-field proof,
complete record ownership or hardware identification is made here.

All six label regions are integrated. Full macOS codec build,254 tests and
package artifact verification pass.52 retained bytes are now source data;
firmware bytes and hashes are unchanged. Device descriptor ownership remains
separate and incomplete as described above.
