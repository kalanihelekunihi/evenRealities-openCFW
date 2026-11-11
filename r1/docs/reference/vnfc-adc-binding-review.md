# VNFC ADC averaging handle correction

Stock averaging at `0x50c90` loads the standalone `vnfc_rect_adc` cache at
`0x20006854`. Its C body previously loaded the VBAT runtime field at
`0x200068a0`. It now uses the existing VNFC owner in `i2c5/stock_transport.c`.
The pointer is volatile so each open/read/close observes a fresh cell load.
No duplicate data owner or manifest unit was added.

REA readback of the locked image confirms the literal `0x20006854`. The new
fixture places VNFC, VPMIC (`0x2000688c`) and VBAT cells at their actual distinct
addresses with distinct handles. All 224 paired averaging cases pass, including
partial writes, negative clipping, callback handle mutations and error returns.
Both other cells remain unchanged. The previous compiled object is rejected on
its first VBAT-cell read. All 65,536 isolated scaling inputs still pass.

All 579 R1 units compile with no known failures or duplicate strong symbols;
imports remain 164 application / 34 bootloader. Only averaging and I2C5 transport
objects change. The latter changes registration ordering: ADC cache store now
precedes the bus-cell load, matching native `0x50474` then `0x50478` ordering.
The cache initializer itself remains unchanged.

The 32-byte exposed frame bridge remains assembly; the private C helper frame
still differs from stock. Driver/delay boundaries are modeled. Physical ADC
behavior, timing, arbitrary aliases and complete source-only byte identity are
unproven. Probe scripts and REA evidence are under
`build/goal-r1-vnfc-adc-binding`; durable results are in the adjacent JSON.

## Actual cache initialization and direct C boundary

The actual native and C cache initializers followed by averaging pass another
224 paired cases. Each starts with a preseeded VNFC cell: lookup must use
`vnfc_rect_adc` and replace it before averaging; the two other ADC cells remain
distinct. Registry lookup, ADC dispatch and delay providers are modeled.

A direct C root using the shared SP observation helper achieves the native
32-byte exposed frame and all provider live R4–R11 values. Its 224-case bounded
suite passes when the first eight stack-word stores are excluded. The strict
ordered-access suite rejects it: native pushes saved R3/sample first, then
R4–R9/LR, while C stores the sample after the other seven saves. This exclusion
is diagnostic only and does not authorize the replacement. The original bridge
is retained. A natural local-variable version additionally requires 40 bytes.
