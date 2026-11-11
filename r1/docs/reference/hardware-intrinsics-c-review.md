# R1 hardware task and watchdog BASEPRI intrinsics

The failure paths in `board/native_tasks.c` and
`board/native_watchdog_manager.c` now use
`__builtin_arm_wsr("basepri", UINT32_C(64))` instead of handwritten
`msr basepri` statements. This extends the preceding
[Cortex-M intrinsic review](cortex-fault-c-review.md) to two more
such statements in the reviewed hardware units. The watchdog's separate incoming
and outgoing R3 capture boundaries remain unchanged; this step does not remove
all assembly from that unit. [Machine receipt](hardware-intrinsics-c-review.json).

Both complete objects are byte-identical to their preceding versions. The
watchdog's flag update, BASEPRI write, fault-record publication and faulting
store therefore retain their compiled ordering. The hardware task failure
paths also retain their compiled instructions. This proves preservation of
these C candidates under the configured Clang compiler, including their
previously documented limitations; it does not prove equivalence to every
stock instruction or real exception behavior.

The full R1 source build passes: 603 units compile, both relocatable
compositions pass, and there are no failures or duplicate strong symbols.
All 603 objects and both composition outputs are byte-identical to the
preceding build. The manifest, import sets and canonical source plan are
unchanged: 160 application imports and 34 bootloader imports remain.

No new source bytes were admitted. The preceding hybrid output was read back
and verified against the locked application and the unchanged source-plan
hash. A redundant hybrid rebuild or behavioral replay was not needed because
all compiled objects are unchanged. Compiler support beyond configured Clang,
source-only completion and physical hardware behavior remain unproven.
