# Independent review 6495

Disposition: **PASS_SCOPED**; `accepted:false`.

The fixture's pinned firmware SHA-256 matches the locked image, and its replay file hash matches the receipt. I checked the oracle against the two reviewed leaf instruction sequences: it covers every 16-bit input for each helper with fixed high bits `0xA5A5`, checks unchanged R0/no write for negative mask-helper inputs, and checks word index plus one 32-bit mask store for nonnegative inputs. For the byte helper it checks signed-index routing, the positive-base byte store, the negative-base offset store, the R0 return value, and low-byte truncation of the shifted R1 value. The recorded counts total 131,072 cases.

I could not rerun the Unicorn execution because Unicorn is unavailable in this environment (`ModuleNotFoundError`). This review therefore validates the pinned fixture and oracle logic statically, not its recorded runtime outcomes. It does not establish hardware behavior or extend the reviewed leaf routines' scope.

No canonical files or gates changed.
