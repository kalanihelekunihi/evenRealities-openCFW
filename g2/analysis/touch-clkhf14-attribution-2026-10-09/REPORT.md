# HF source selection: historical divider names corrected by bytes

Three unchanged authentic public-source functions link exactly:
ExtClkGetFrequency `[0x9C38,0x9C44)` 12 bytes;
ClkHfGetSource `[0x9F34,0x9F44)` 16 bytes;
ClkHfSetSource `[0x9F44,0x9F9C)` 88 bytes. All116bytes await independent review.
Original symbols remain untouched. The last two historical rows call them
GetDivider/SetDivider; source names and bit behavior disprove that attribution.
The independent historical SetSource row at `0xA188` remains unresolved and
must not be silently dropped or merged into the corrected rows.

GetSource reads source bits0–1. SetSource rejects values >1 with status
`0x4A0001`, returns success without writes when the selection already matches,
accepts IMO only when its readiness bit is set, and accepts external clock only
when the configured frequency is nonzero. Unready source returns `0x4A0003`.
Otherwise it preserves other clock-selection bits and writes source bits0–1.
This is source selection, not divider setting.

ExtClkGetFrequency loads a software word at `0x20000F20`; the original LDR and
zero-addend section relocation bind that location. No frequency value was
invented or measured. Original BL at `0x9F50` and `0x9F6C` bind the two helper
functions. Static exactness establishes instructions and interface semantics,
not physical oscillation, clock switching safety or firmware-wide completeness.
Linker commands, literal/call evidence, source-object and ELF hashes are in
`results.json`; no manual byte patches or runtime implementation additions.
