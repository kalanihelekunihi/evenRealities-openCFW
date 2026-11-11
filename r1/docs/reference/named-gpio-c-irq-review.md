# Named GPIO shared-pin IRQ verification

The current pure-C dispatcher matches the tested stock behavior at `0x6ed94`.
No firmware edit is needed for this boundary. Fresh REA analysis and raw
instructions show a seven-record walk: load pin, compare the full input pin,
load the callback only on a match, skip null callbacks, pass the low pin byte
and action word, then continue to later records. The opened flag is not tested.

All 19,776 stock/C comparisons pass. Cases vary event pins including full-width
values, action words, record match masks and every seven-bit callback mask.
Controlled callbacks clobber caller-saved registers and can enable a later
record, clear its callback, change its pin or replace its callback. The later
record is reloaded and observed as stock does. The shared P1.01 case invokes
record indices 4 and 6 in order, covering both pmic_irq and device_stacmd_irq
positions in the locked configuration.

Checks compare ordered pin/callback memory reads, callback identity and
arguments, complete controlled record storage, R4-R11, SP, interrupt masks and
8-byte callback alignment. IRQ callbacks are modeled; the actual stock and
compiled C dispatch loops execute. This is not physical GPIOTE delivery,
asynchronous thread/concurrency coverage, complete fault equivalence or byte
qualification. Both functions being 52 bytes does not establish byte identity.

The source hash is verified against the latest 562-unit R1 build report. The
firmware source, manifest, source plan and G2 gates remain unchanged in this
verification round. Exact executable, REA, probe and source bindings are in the
[machine-readable review](named-gpio-c-irq-review.json).
