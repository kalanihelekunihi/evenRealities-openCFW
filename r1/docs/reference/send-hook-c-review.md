# Send-hook dispatcher in ordinary C

The dispatcher at stock `0x827f8` now uses a three-argument function pointer
matching the registered C fragment sender. The empty assembly constraint on
the null path is removed. It loads the existing volatile hook once, returns
`UINT32_MAX` when null, otherwise forwards handle, packet and length unchanged
and returns the complete callback result. Callback replacement of the slot
survives the call. Native R3 holds the branch target as an instruction side
effect; it is not part of this public C callback signature.

REA confirms the fourteen-byte body and slot `0x20006c20`. All 2,144 stock/C
comparisons pass, including full-word arguments/results, null hooks, live slot
mutation and callbacks that clobber integer/FP scratch registers. All fourteen
native instruction bytes execute. Preserved integer/FP registers, SP, masks,
slot and guards are checked; incidental caller-saved values and private stack
layout are excluded.

A separate transport replay routes generation through the actual dispatcher
and actual C fragment sender, then CRC/memory/receiver bodies. It passes 1,355
compatible stock/C comparisons, all 34 lengths from 4,063 through 4,096 and
16 safety cases. The extended lengths intentionally improve on stock RX.
Services and final delivery callbacks remain modeled.

All 852 translation units compile and both relocatable payloads compose.
All 841 other nongenerated objects are unchanged. Imports remain 66 application
and 22 bootloader symbols. R1 manifest validation passes. Final linking,
physical radio delivery and boot remain unverified.

[Machine evidence](send-hook-c-review.json) binds REA, sources, replay and builds.
