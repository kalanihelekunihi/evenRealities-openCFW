# Append-only correction for independent review 2645

The prior review converted receipt value `536871256` incorrectly. That decimal value is `0x20000158`, not `0x20000098`. The authenticated literal at `0x42ACBC` and the replay agree on `0x20000158`; the replay writes controlled entries into slots 0 and 26 at that address. This is a reviewer prose conversion error only. The candidate and replay are correctly bound, and the scoped routing result remains valid for those controlled entries. The correction does not establish actual handler semantics or extents. `accepted` remains false.
