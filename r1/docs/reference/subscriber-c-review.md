# R1 subscriber synchronization and consumer control in C

The subscriber mutex wrappers and consumer control flow now use C. The redundant
`r1_subscriber_current_thread` assembly bridge is removed: the consumer and
multicast caller use the existing canonical CMSIS `osThreadGetId` implementation.
That selected C function already supplies the stock `0x7d814` region in the source
plan. Its normal instruction body and relocation are identical to the removed
bridge; this does not add another implementation of the same stock function.

`native_subscriber_sync.c` uses the pinned CMSIS `osMutexAttr_t` and `osStatus_t`
types, with compile-time layout/width checks. Lock samples the shared mutex cell,
creates a mutex if zero, stores the creation result and acquires it with
`osWaitForever`, even if creation returned zero. It does not reload the cell
between storing that result and acquisition. Unlock samples the cell again and
returns the release status, or osOK when zero. Return words are not narrowed.
The old mutex/control/name/attribute sections retain their bytes, sizes,
alignment, flags and relocations. Their addresses remain `0x20006794`,
`0x2001571c`, `0xbf784` and `0x99bb8` in the probes. Only the two C units use a new
manifest profile derived from the old profile plus C11, function/data sections
and the pinned CMSIS include directory.

`native_subscriber_consume.c` captures the current thread before locking, reads
the event head after acquisition, skips owner reads for null callbacks, and
invokes only matching-thread callbacks with event +6. After each callback it
reloads the event head before reading next and updating the event's head word.
A callback clearing that head therefore still causes the native read fault at
address +8, rather than a new sanitized exit. Unlock retains a late mutex-cell
reload and its native return word. The multicast caller's instruction bytes are
unchanged; its sole changed relocation names the canonical CMSIS function.

## Retained callback ABI boundary

Callback descriptors contain raw target words, and a single compatible C
signature has not yet been established for all targets. A two-byte `BX R1`
gateway therefore remains, preserving the raw R0 payload and R1 target rather
than making a call through an unproven C function-pointer type. Its memory
clobber makes callback side effects visible to the C control flow. It is an ARM
ABI helper, not an empty callback implementation. This is a partial consumer
conversion; callback-signature review remains before eliminating that boundary.

## Verification

The normal build passes 3,034 paired stock/C emulator cases: 270 each for lock,
unlock and canonical thread ID, plus 2,224 consumer cases. Actual C CMSIS thread
ID and FreeRTOS current-task getter code execute. Mutex APIs and opaque callbacks
are modeled; execution of their other kernel dependencies is forbidden by the
probe. Cases cover creation failure, callback mutation of the creation cell,
full-width status returns, thread capture before lock, acquisition changing the
head/current thread, callback replacement or clearing of the head, changes to
next/owner/mutex words, overlapping owner/event storage, unaligned records,
invalid owner/null-head faults, null events and null callbacks. Ordered shared
accesses, native callback R0/R1, final guards/state, return SP, saved registers
and interrupt masks agree. XPSR/IT state resets per invocation. Negative controls
for late thread sampling and a stale event head are rejected.

A separate startup check executes the locked RW decompressor and ZI clearer,
checks the scatter table and whole-region guards, and cross-checks an independent
RW decoder. The existing four-byte mutex cell and 80-byte control storage match
84 native zero bytes. Linked source attributes and the 12-byte mutex name also
match stock. This does not establish complete startup placement or execution.
REA/Ghidra observes the two mutex routines and the thread-ID thunk; its default
database lacks the consumer entry. That error gives no coverage credit. The
consumer uses direct locked Thumb disassembly/execution and a supplemental
frontier row with native caller entries. These local observations do not
establish corpus coverage.

All 575 R1 units compile without failures or duplicate strong symbols. Imports
remain 175 for the application and 34 for the bootloader. Other object bytes are
unchanged. The manifest changes only two unit profiles and adds their shared
profile; no source unit is added. Fifteen qualification candidates compile
(three units across five profiles). Only the unchanged assembly multicast body
qualifies; it was not promoted, and the new C mutex/consumer code remains
unqualified. The existing canonical thread-ID selection stays in place.

The source plan is unchanged. A fresh hybrid still equals the locked 646,408-byte
application: 3,881 source-built bytes, 642,279 binary pull-through bytes and 248
resource bytes. These are stored-byte provenance counts, not executable-C
coverage, admission of the new C routines into the hybrid or source completeness.
Actual mutex scheduling, queue routing, physical sensors, asynchronous execution,
private stack traffic and caller-clobbered registers/flags remain outside this
probe. No G2 source or workflow gate changed.

See [subscriber-c-review.json](subscriber-c-review.json) for hashes and paths.
