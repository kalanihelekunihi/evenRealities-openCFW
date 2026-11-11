# Task-priority setter C dependency review

The selected mutex-task unit now includes pinned FreeRTOS 10.5.1
`vTaskPrioritySet`, corresponding to stock entry 0x96314 (198 instruction
bytes). Local macros provide the existing native task-handle convention and
pinned port yield operation. The 104-byte accessed TCB prefix and 56-priority,
nonoptimized ready-list configuration are shared with the checked mutex paths.
No alternative task layout or hand-written assembly body is introduced.

[Machine-readable evidence](task-priority-c-dependency-review.json) binds the
REA instruction evidence, source selection, differential probe, negative
controls, audit, source build and hybrid report by SHA-256. REA confirms the
invalid-priority BASEPRI/fault path, base/inherited-priority distinction,
ready-list removal/insertion and yield sequence. The locked instructions
request PendSV and execute SEV, DSB and ISB; this takes precedence over
pseudocode that omits SEV or suggests a privilege-dependent assertion.

The actual stock and C priority-set/list-remove/ready-insert algorithms agree
in 7,236 paired cases (14,472 executions): 7,200 valid cases and 36 assertion
cases. Coverage combines normal/inherited priorities, new priorities across
raise/lower/equal boundaries, current/other/null task handles, ready/blocked
list membership, list-index choices, reserved/nonreserved event values,
top-ready priorities and interrupt masks. Snapshots cover guarded task records,
all 56 ready lists, the blocked list and scheduler cells. The probe compares
critical-boundary observations, PendSV writes, SEV/DSB/ISB order, final SP,
callee-saved registers and interrupt masks. Independent assertions check the
new effective/base priorities, event value and yield decision. Invalid
priorities 56, 0x7fffffff and 0xffffffff fault with the observed mask/address/
width/value before entering the critical section. Controls that lose inherited
priority, overwrite a reserved event value or omit yielding are rejected.

Critical entry/exit are modeled. Valid initialized task/list relationships are
required; malformed-pointer/list faults, complete exception state, asynchronous
scheduler execution and physical concurrency remain unverified. Caller-clobbered
words/flags and private frame identity are excluded. The source uses the actual
compiled list-removal body, not a replacement list model.

All three preexisting mutex-task function bodies remain byte unchanged. All
573 R1 units compile without failures or duplicate strong symbols. Application
imports fall from 182 to 181, resolving only this function; bootloader imports
remain 34. Five qualification profiles select no exact regions. The canonical
source plan remains at 3,857 source-built bytes, 642,303 binary-pull-through
bytes and 248 resource bytes. The hybrid still equals the locked application
byte for byte. This function is behaviorally checked but not byte-qualified;
complete source linking and hardware execution remain unfinished. No G2 corpus
gate advances.
