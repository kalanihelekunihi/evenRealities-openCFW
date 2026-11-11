# Current-task event-item reset in C

The selected unordered-event task unit now owns `uxTaskResetEventItemValue`
(stock 0x95738). It returns the current event-item value and restores the normal
priority-derived value for subsequent queue/semaphore use. The pinned FreeRTOS
10.5.1 body supplies the algorithm; explicit C accesses preserve stock ordering.

REA confirms 20 instruction bytes. Stock reads `pxCurrentTCB` twice, reads the
first task's event value and second task's priority, reads `pxCurrentTCB` again,
and writes `56 - priority` to the third task's event value. The literal binds
the cell to 0x2000781c. Volatile typed accesses retain these three observations;
no handwritten assembly is added. The baseline-profile upstream body orders
its field read between the first two pointer reads and fails the trace test.

[Machine-readable evidence](event-reset-c-dependency-review.json) binds sources,
REA observations, probes, negative controls, source builds, qualification and
both merged/canonical hybrid reports by SHA-256. The normal and qualified Oz
profiles each pass 3,456 stock/C comparisons (6,912 executions per profile).
Every combination of three task-pointer choices is covered, with boundary
priority/event words and four interrupt masks. Hooks compare the complete
ordered data-access trace and guarded task-record bytes, return value, SP,
callee-saved registers and interrupt masks. Negative controls reject the
unadapted upstream ordering, cached task pointer and wrong priority constant.
Pointer replacement is synchronous probe injection, not proof of asynchronous
scheduler behavior. Valid aligned task records are required; malformed-pointer
fault state, caller-clobbered words/flags and private frame identity are excluded.

Both preexisting function bodies in the unit remain byte unchanged. All 573 R1
units compile without failures or duplicate strong symbols. Application imports
fall from 183 to 182, resolving only this function; bootloader imports remain 34.

The official qualifier tested five profiles. Oz produces an exact 24-byte
region: 20 instruction bytes plus the four-byte current-task-cell literal.
After a nonoverlapping merged plan produced a fully stock-identical application,
that selection was promoted into the canonical source plan and rebuilt again.
The canonical hybrid remains byte-identical. Source-built bytes increase from
3,833 to 3,857; binary-pull-through decreases from 642,327 to 642,303, with 248
resource bytes unchanged. This local exact result does not prove source
completeness, complete source linking or physical hardware execution. G2 corpus
gates and global frontier completeness remain unchanged.
