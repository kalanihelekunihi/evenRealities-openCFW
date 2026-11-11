# C pending-tap timeout and gesture entry

The timeout at stock `0x8e9d0` now has a C implementation in the existing
release unit. A pending contact clears bytes 48 and 0, then dispatches the fully
initialized record `{4,0,contact[95],0}`. The existing timer-pending byte is
cleared after dispatch, including callback mutations and the inactive path.
That byte already owns stock `0x200067c4`; no new phase or contact owner is added.

The gesture entry at `0x3e938` now supplies an aligned twelve-byte C packet frame
instead of using an assembly bridge. Its existing kernel is unchanged.

The [review receipt](touch-pending-c-review.json) records 3,956 direct stock/C
comparisons and 1,496 comparisons with actual C gesture handling, including 48
staged timer-message/queue/timeout/gesture cases. These cover every gesture flag,
nonboolean pending values, direction/count/time wrap, packet sizes, repeated live
connection reads and provider mutations. Eight compiled defects are rejected,
followed by an unmodified integration rerun. Real standard memory routines execute;
callee-saved integer/FP registers, stack guards and interrupt masks are checked.
FIFO and lower services remain models; the kernel queue backend is not exercised.
REA byte reads match the pinned stock image. The attempted slider pseudocode
operation failed and is not treated as completed slider evidence.

The normal build compiles 840 units (758 application and 82 bootloader), with
73 application imports and 22 bootloader linker imports. One import closes and
none are added. All 836 other objects are unchanged, including eight generated application
objects. The gesture
kernel, prior release code and allocated state sections retain their bytes;
only the gesture entry and newly added timeout sections change. The R1 manifest
check passes. Global `make sources-check` still fails on the pre-existing unlisted
G2 `resident_rom_thumb_set.S`. Final linking, runtime placement, physical timing
and device boot remain unverified. Byte identity is not required.
