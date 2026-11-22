# Touch configuration bootstrap — offline reconstruction

Independent source for bootstrap0x395c, application adapters0x3520/3568/35b0,
EEPROM erase0x8ae0 and software delay0xa2f0. Fixed ARM32 guest addresses;
this module composes the preserved `eeprom_offline` and `eeprom_init_offline`.
It is linked into the current source-candidate touch image; no production
firmware or hardware behavior is validated by that link.

The nine locked bootstrap/save log strings now have C-owned definitions,
including the shared color reset string. Their linked bytes match stock and
the calls no longer retain fixed pointers into the old flash tail. The stock
logger remains a return-zero leaf. See
[`touch-log-strings-source-20261111.json`](../../../evidence/touch-log-strings-source-20261111.json).

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
