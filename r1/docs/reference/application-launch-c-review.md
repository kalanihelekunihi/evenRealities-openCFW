# Application RTOS launch lifecycle in C

The application entry no longer loads its launch callback from the absolute
RAM address `0x20006540`. It references the start field of a source-owned,
relocatable twelve-byte lifecycle record. Its initial callbacks are ordinary
C implementations of stock launch `0x45e64` and stop `0x45e4c`, followed by
the initially null manager-thread handle. Existing entry bytes/relocations
change only where that callback address is materialized and recorded.

The launch routine calls kernel initialization and ignores its result, creates
the transient startup thread with null argument/default attributes, then
starts the kernel. Thread-creation failure uses the existing shared fault
primitive. The transient thread at `0x45e90` creates the manager worker using
the recovered attributes, stores the handle before testing failure, obtains
its own thread ID and terminates itself. It does not terminate the manager.
Stop captures the manager handle once, conditionally terminates it, then
clears the live field even if termination reports an error or mutates it.

The manager's name, 112-byte TCB, 2,048-byte stack, priority 53 and trust-zone
module field 1 have typed C owners. Its official CMSIS attribute layout is
checked at compile time. REA authenticates the complete three-routine window
and literals. Raw ROM attributes and previously authenticated initialized
RAM bytes agree with the recovered lifecycle and attribute fields. TCB and
stack storage are aligned source BSS; physical initialization is not proved.

216 stock/C comparisons cover initialization results, creation results,
kernel-start results, self IDs, termination statuses, zero/nonzero handles,
live handle mutation and both PRIMASK settings. Actual allocation failure
code sets BASEPRI to 64 and attempts the stock zero write to `0xffffffff`;
the fixture observes that access. Private fault frames/exception snapshots
are excluded. Sixteen additional cases execute the actual source application
entry through the relocated callback, including replacement of the live
callback. Other entry services and CMSIS functions are modeled.

Four compiled defects fail behavioral assertions: gating launch on kernel
initialization error, omitting manager attributes, terminating the new manager
instead of self, and clearing the manager handle before termination. The
normal fixture is rerun afterward. Normal returns preserve SP, callee-saved
registers and masks. Void/caller-clobbered outputs are excluded.

All 803 R1 units compile with no failures or duplicate strong symbols. The
799 other prior object hashes are unchanged; two generated boot objects
retain source hashes, allocated bytes and relocations. Entry retargeting is
limited to its MOVW/MOVT address pair, callback descriptor and their three
relocations. Strict bootloader linking and R1 source checks pass; global
source checking retains the unrelated unlisted G2
`resident_rom_thumb_set.S` failure.

The worker body at `0x45d7c` is deliberately an explicit unresolved
`r1_application_manager_thread` dependency. Consequently application imports
increase from 68 to 69 as this previously hidden absolute-target path enters
the C graph. Real task creation/scheduling, full manager behavior, reset/vector
completion, initialized-data/BSS startup, physical boot and full application
linking remain unfinished. No source-plan selections change. See the
[machine-readable review](application-launch-c-review.json) for exact evidence.
