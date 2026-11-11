# Named SAADC sample frame repair

`r1_named_adc_sample` at stock address `0x548f0` now uses a C lookup/sample
body with an explicit saved-R3 frame bridge in `stock_named_adc.c`. This
removes an uninitialized C sample local. Stock ignores conversion status and
copies the low half of its saved-R3 word, even when conversion writes nothing.
The old compiled candidate used a local at entry SP-22; stock uses SP-24.

REA confirms the native lookup order: load the device name, load each record
name, compare, then load the matched record's opened byte. The C body uses
ordered volatile views so callbacks can change names or opened state between
steps. An absent or closed record returns 8. An open match invokes conversion
with the record index, ignores its status, writes the scratch halfword to the
original output pointer and returns zero. No extra guard or zero sample is
introduced.

The 10-byte bridge captures incoming R3 at entry SP-24 and restores its final
word. The C body is 76 bytes with the current compiler; the native routine is
76 bytes. The native sample/output access widths are retained. If output
aliases either scratch halfword, its write also affects the restored R3 word.

The ignored `build/goal-r1-adc-sample/verify.py` probe passes 1,508
stock-versus-C cases. They cover every seed byte, partial/non-writing
conversion responses, full-width conversion statuses, all three channels,
missing/closed records, live name/opened changes, output aliases and guards,
and caller-saved register/flag clobbers. Checks include exact data-read order,
I/O arguments, native scratch address, halfword accesses, R0/R3, callee-saved
registers, SP, interrupt masks and callback alignment.

A before-image probe with a non-writing conversion and incoming R3 of
`0xaabb1234` observes the old SP-22 pointer and output `0x5a5a` under a
deterministic stack fill. Stock and the repaired code use SP-24 and output
`0x1234`. This demonstrates the reconstruction mismatch, not particular
contents of a physical device's stack.

The other three ADC function bodies, operation-table relocations and cold
record bytes/alignment are unchanged. All 562 R1 units compile without
failures or duplicate strong symbols; imports remain 227 application and
34 bootloader. Exact source, manifest, native, REA and probe bindings are in
[the machine-readable review](adc-c-sample-review.json).

String comparison and conversion API boundaries are modeled. The C body adds
private callback stack depth. Physical SAADC measurement, analog accuracy,
timing, complete flag/fault equivalence, final linking, provider qualification
and byte identity remain unproven. No G2 gates or source-plan selections change.
