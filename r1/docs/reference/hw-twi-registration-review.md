# R1 hardware-TWI shared layout and registration

Six hardware-TWI modules now consume `native_hw_twi.h` instead of repeating
their control/record/cluster layouts. The header asserts the 12-byte control,
96-byte record, 108-byte cluster, semaphore/result positions and operation
slots. Registration's old `void(void)` declarations differed from the actual
definitions: open/close return a word, read/write take three arguments and
return a word, and completion helpers take an event pointer and return a word.
The shared declarations now match those definitions, with typed heterogeneous
operation slots. All six translation units produce identical allocated
sections and normalized relocations before and after this consolidation.

The IRQ slot remains explicitly opaque. The native completion helpers and
Nordic's two-argument, void-returning callback type differ. The existing
native binding remains explicit; this change neither invents a callback ABI
nor claims that casting between those signatures establishes compatibility.

The registration provider now participates in relocatable composition. REA
and assembly identify the primary record at `0x20006FF4`, its preceding
control at `0x20006FE8`, and the secondary pair at `0x20007060`/`0x20007054`.
Registration publishes the name and operation table, calls the registry,
creates a binary semaphore with `(1, 0, NULL)`, stores the result, and sets
the bus-specific ready byte only on success. Failure leaves an existing
ready byte intact. Primary uses control +2; secondary uses +1.

Direct stock-versus-source execution passes 162 cases covering both buses,
existing ready values, semaphore success/failure, ignored registry statuses
and ready-byte mutation during the semaphore call. Checks compare return
values, complete 108-byte controlled cluster snapshots and state visible at
each provider call. Test-only hook symbols replace registry/semaphore calls;
metadata operation callbacks are not invoked. This does not validate native
scatter seeds or physical transfers.

REA observes 46-byte bodies at `0x54F90..0x54FBD` and
`0x54FC4..0x54FF1`, inclusive. Historical 44-byte provenance entries omit
the final two-byte `pop` return. This discrepancy is recorded here without
altering accepted pseudocode coverage or canonical ledgers. Decompiler
signatures also omit the zero third semaphore argument and machine return
value; assembly and execution provide those details.

All 561 R1 units compile and both payloads compose. The two control-record
imports resolve, reducing application imports from 244 to 242; bootloader
imports remain 34, with no new imports or duplicate strong symbols. No
source-plan entry or workflow gate changed. Final firmware linking, complete
source identity, native callback ABI closure and hardware validation remain
open.

[hw-twi-registration-review.json](hw-twi-registration-review.json) binds the
shared header, source/report hashes, six-object comparison, REA observations
and execution results. Probes and the neutral REA snapshot remain under
ignored `build/goal-r1-hw-twi/`.
