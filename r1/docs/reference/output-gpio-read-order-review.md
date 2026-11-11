# Output GPIO lookup read order

`gpio/native_output_gpio_operations.c` now explicitly loads the caller device
name before the candidate record name. The previous `strcmp(record->name,
device->name)` expression did not order its two volatile reads; the current
compiler loaded the record name first. Stock configuration slot `0x54cd0`
and read slot `0x54e20` load the device name first. REA for the configuration
slot and raw instructions/execution identify the corresponding reads.

A controlled mutation demonstrates the difference: device name initially
selects record 0, then changes to record 1 when record 0's name is loaded.
Stock and corrected C retain the earlier device-name value and select record
0. Previous C observes the changed name and selects record 1, writing its
configuration instead. This establishes a semantic discrepancy; it does not
establish how often such mutation occurs on a physical device.

All 214 stock/C comparisons pass. Cases cover both operations, five records
and a missing name, closed/open states, pins 0/31/32/36/63, both GPIO ports,
null configuration, overlapping configuration storage, and controlled name
mutation. Checks compare the exact ordered name reads and comparison arguments,
complete controlled configuration and output guards, raw return values, the
read operation's saved R3, R4-R11, SP, interrupt masks and callback alignment.
The Nordic port decoder and GPIO accesses execute; strcmp is modeled and GPIO
registers are ordinary emulator memory.

All 562 R1 units compile without failures or duplicate strong symbols.
Imports remain 211 application / 34 bootloader; the other 561 units are
unchanged. The source plan and G2 gates remain unchanged. This does not prove
physical GPIO behavior, concurrency/fault equivalence, byte identity or a
complete source-only firmware build. Inputs and hashes are bound in the
[machine-readable review](output-gpio-read-order-review.json).
