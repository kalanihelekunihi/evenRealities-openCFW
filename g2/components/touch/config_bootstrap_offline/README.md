# Touch configuration bootstrap — offline reconstruction

Independent source for bootstrap0x395c, application adapters0x3520/3568/35b0,
EEPROM erase0x8ae0 and software delay0xa2f0. Fixed ARM32 guest addresses;
this module composes the preserved `eeprom_offline` and `eeprom_init_offline`.
It is not linked into production firmware or accepted checkpoints.

Saved record is8 bytes: little-endian magic0x45564e55,baselineu16,parameteru16.
A successful read plus matching magic accepts the record. Parameterzero becomes1000
in RAM only. Other field values are not range-validated. Failed read or bad magic
starts erase→delay(argument10)→default record write; each upper error aborts.
Library readiness and valid saved-record contents are separate.

Erase for the installed row=sector128 extended geometry writes a checksum-bearing
empty row with incremented sequence into all main/mirror wear rows. It is not
an all-zero physical erase. Sector>row wrapping is outside this implementation.
Physical SROM responses/storage effects and scheduling remain unverified; elapsed
units are not inferred from delayargument10. See the associated analysis report
for original-instruction receipts, failure fixtures and coverage limits.
