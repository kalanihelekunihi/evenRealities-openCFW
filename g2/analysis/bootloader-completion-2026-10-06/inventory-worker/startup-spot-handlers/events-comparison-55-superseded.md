# Superseded event comparison note

The earlier 55-case comparison receipt is superseded for the range-handler claim. Its dispatcher loop overwrote every `42d562` fixture's state pointer with `DATA+0x100`; selector-2 tests therefore read zeroed state bytes instead of the float tuple initialized at `DATA`. Since output endpoints were stored beyond the reported float snapshot, the apparent matches were inert for range classification.

The corrected harness preserves explicit/default state pointers and adds direct `42ced8` float cases. The current authoritative receipt is `events-comparison.json` (72 cases). `events-comparison-55-superseded.json` preserves the 55 inert outcomes with an explicit `SUPERSEDED` status. It is a reproduction using the current linked source ELF, not a byte-for-byte copy of the earlier receipt or its ELF. Neither receipt is treated as evidence for float range behavior.
