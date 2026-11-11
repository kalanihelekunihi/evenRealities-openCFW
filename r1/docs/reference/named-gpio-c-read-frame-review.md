# Named GPIO lookup and input-read frame

`gpio/stock_named_gpio.c` now reloads the device name before the candidate
record name through explicit volatile views. Stock callback registration
`0x54afc`, close `0x54b40` and input read `0x54ed0` perform those ordered loads
each iteration. The previous C expression left the order unspecified. The
shared lookup is also used by open; its downstream initialization is outside
this probe's scope.

Input read now retains stock's saved-R3 scratch word at entry SP minus 24.
A 10-byte ABI bridge supplies that word to a C kernel. The kernel finds the
record, stores its pin in the saved word, executes the attributable Nordic
port decoder, reads GPIO IN and writes the selected bit. On return the bridge
restores the decoded pin to R3. Missing-name returns retain incoming R3.
The previous scalar `r1_twi_gpio_read` call lost this native saved-word behavior.

All 375 stock/C comparisons pass across the three operations, seven records
and a missing name, closed/open values, pins 0/31/32/33/63 and controlled name
mutation. The mutation reproduces wrong-record callback storage in old C;
an independent normal read reproduces the old R3 discrepancy. Comparisons
include raw R0 and read R3, ordered name reads, comparison/provider arguments,
complete controlled record storage, output guards, R4-R11, SP, interrupt masks
and provider-call alignment. strcmp and GPIOTE close calls are modeled;
Nordic port decoding and GPIO accesses execute against emulator register memory.

All 562 R1 units compile with zero failures or duplicate strong symbols.
Imports remain 211 application / 34 bootloader, the other 561 units are
unchanged, and source checks pass. No source-plan selection or G2 gate changed.
Physical GPIO, interrupt timing, complete fault/concurrency equivalence,
native byte identity and final source-only firmware remain unproven. Exact
bindings and old-source counterexamples are in the
[machine-readable review](named-gpio-c-read-frame-review.json).
