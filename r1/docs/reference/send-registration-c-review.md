# Transport send registration in ordinary C

The callback setter at stock `0x83448` now uses ordinary C instead of fixed
register bindings and empty assembly constraints. Null registration returns
`UINT32_MAX` and preserves the previous callback; nonzero registration stores
the complete pointer word and returns zero. The existing volatile slot is reused.
The C port initializer consumes no caller-saved register values from this call.

REA confirms the sixteen-byte native body and its slot at `0x20006c20`.
All 1,620 stock/C comparisons pass, covering null/nonzero callback words,
previous slots and register seeds. Every native instruction byte executes.
The probe checks result, slot/guards, preserved registers, stack pointer and
interrupt masks, and rejects execution of stock code by the C path. Incidental
caller-saved registers and private stack layout are outside the C contract.

All 852 units compile and both relocatable payloads compose. All 841 other
nongenerated objects are unchanged. Imports remain 66 application and 22
bootloader symbols. R1 manifest validation passes. Physical radio delivery,
complete firmware linking and boot remain unverified.

Flash wrapper constraints remain: their later partial-read consumers can observe
stale stack contents, so removing them requires a coupled read-path change.

[Machine evidence](send-registration-c-review.json) records sources, REA,
replay and build hashes. No source qualification or byte identity is claimed.
