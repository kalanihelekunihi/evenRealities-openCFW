# G2 Touch MIT clean-room Em_EEPROM admission (batch 25)

Eleven authenticated Em_EEPROM boundary functions, including the previously
misclassified `0x4B44` simple-read path, are replaced by independent MIT C.
The admitted boundary covers 1,636 instruction bytes.

The replacement supplies bounds-checked simple storage, CRC-8 (`0xFF` seed,
`0x31` polynomial), row geometry, sequence-based wear selection, checksum
fallback, partial read/write, erase, and adapters matching the existing Touch
storage-provider ABI. All flash operations use a caller-supplied backend; no
fixed address or vendor implementation is embedded.

Host tests exercise simple read/write/erase, extended row rotation, corruption
fallback, CRC, geometry, bounds, and null contracts. The same C compiles for
Cortex-M0+. No Infineon EULA source was copied.

The clean-room extended-row format is not claimed binary-compatible with
existing Infineon-formatted rows. Migration and live flash endurance remain
blocked by unavailable physical evidence because no authorized responsive G2
Touch device or EEPROM capture is available. The source is not yet
production-routed and no flash operation was performed.
