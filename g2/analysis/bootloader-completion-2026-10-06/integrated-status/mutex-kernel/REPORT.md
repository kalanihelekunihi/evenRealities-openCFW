# Native mutex acquisition, recursion and priority bookkeeping

Immutable candidate `681c13c6f3079412efb46ff17aba6afcd7d80fef293418613d772c48448bd7d4`; locked original bootloader `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, load410000. All seven exact-image cases PASS;619 inputs/156 objects unchanged. Previous3fcec29f preserved. [Validation](../same-image-validation-681c13.json).

[Reconstructed kernel C](../../../../components/bootloader/thread_creation/mutex_kernel.c), [helper interfaces](../../../../components/bootloader/thread_creation/mutex_kernel.h), [existing acquire/release C now linked](../../../../components/bootloader/queue/mutex.c). Root MIT license and existing notices preserved; no upstream source copied.

## Native call chain and data layout

CMSIS wrappers4166aa(acquire102B)/416710(release82B) reject interrupt-masked/nonblocking context with-6 and null untagged handle with-4. Handlebit0 dispatches recursive vs plain; timeout is forwarded unchanged. Kernel success must equal1; acquire failure is-2 for nonzero timeout or-3 for zero, release failure-3. The runtime/context predicate is native source.

Recursive419e22(64B) queries current task418b4e(8B). Matching owner increments recursion without another token take; otherwise native plain41a24e(354B) runs and recursion increments on success. Recursive give419de2(64B) returns0 for another owner, otherwise decrements depth and calls native queue put419ec0 only at zero. Counters wrap modulo32bits; owner match with depth0 decrements toffffffff and reports1 without giving a token.

| ARM32 queue offset | Mutex use |
| --- | --- |
|00h|0 marks mutex semantics rather than ordinary zero-sized semaphore|
|08h|owner TCB pointer|
|0ch|recursive depth|
|10h /24h|send/receive waiter list anchors|
|38h /3ch|available token count/capacity|
|40h|item size; plain mutex take asserts it is0|
|44h /45h|signed lock counters, -1 unlocked|

Plain take enters native critical section, consumes an available token, and for a mutex records current owner via418d90(22B), incrementing TCB+64h held-mutex count. It may remove/wake a send waiter. Empty zero-timeout returns0. Nonzero timeout captures tick state, suspends scheduler, locks queue, checks elapsed time, and either inherits owner priority/enqueues on receive list or retries when token appears. Expiration unlocks/resumes; a token appearing at that boundary is still taken. If still empty and inheritance was recorded, priority is reduced only under the recovered single-held-mutex rules.

Inheritance418b7c(162B) raises owner effective priority TCB+2ch to current task priority; event key TCB+18h becomes56-priority unless its highbit marks an in-use value. A task on its old ready list moves to the new ready list using native list unlink. An already-high-enough effective priority still returns1 if base TCB+60h is below the requester. Timeout disinherit418ccc(174B) selects max(base,highest remaining waiter), updates only when exactly one mutex is held, and rejects current-task ownership via fatal assertion. Waiter priority41a492(20B) is0 for empty list or56-headkey.

Plain release delegates to native queue put; its wrapper has no graceful owner mismatch check. For a mutex, existing native queue-copy/release helpers enforce current ownership and nonzero held count via fatal assertion. Releasing the final held mutex can restore base priority and relocate the ready-list node; releasing while other mutexes remain retains effective priority. No new allocation/delete/cancel/free logic was introduced.

## Validation and explicit limits

[516 focused comparisons](../mutex-kernel-681c13.json) compare full80-byte queue, two128-byte TCBs, ready lists, priority globals, return/error values and masks.1052 mapped instruction-body bytes;1002 visited by this suite. Unvisited bytes include fatal spin tails, one fatal current-owner branch, send-waiter wake branch and scheduler-resume==0 yield branch. No whole-body coverage claim. Source machine executes only ELF executable segments and never loads stock code. Native priority/list/critical and queue release bodies execute.

[Two persistent ownership/priority sequences](../mutex-sequences-681c13.json) execute native wrappers and kernel paths across repeated calls. Synthetic CURRENT selection demonstrates recursive retention, wrong-owner recursive release error, competing zero-timeout take failure, final token restoration and final priority/list restoration. It does not prove simultaneous hardware exclusion.

Blocking fixtures explicitly inject timeout check, wait-list enqueue, suspend/resume and queue unlock; token availability is injected at wait enqueue or timeout check. Priority updates themselves are native. Real scheduler restoration, IRQ/tick delivery, task switch, priority inheritance under all wait configurations, cancellation/deletion and asynchronous drain remain unverified. Fatal tests stop at the invalid store after interrupt masking, rather than claiming a recoverable error.1000 is a raw API argument; no milliseconds claim.

## Provider ledger consequence

Two former OTA numeric aliases4166aa/416710 become native bindings: candidate35 aliases/27 addresses =28 aliases at20 OTA addresses +4 synthetic cuts +3 external ROM dependencies. Plain/recursive kernel paths and priority helpers were implicit dependencies, so their recovery reduces real source gaps without being counted as former aliases. Whole-payload completeness remains unknown.

Next worthwhile explicit source boundaries are ISR queue put41a024/get41a3b0 and ISR notify/event flags, with deferred scheduling and ownership kept distinct; alternatively the still-numeric EasyLogger setters and logger/assertion path. This batch does not implement speculative cancellation/drain patches.

The first service-only regression followed old numeric take/give seams; its auxiliary verifier now resolves source symbols while retaining explicit injected APIs. The first CMDQ supplement used a stale absolute critical-save address16c2d; the separate module was relinked from the same frozen object to current16c45. Both failed logs are retained, and the corrected module/provenance are in the candidate snapshot. Neither correction changes the shared ELF or seven-case imported runner inputs.

[Four actual blocking-setup cases](../mutex-block-boundary-681c13.json) additionally execute timeout capture/check, scheduler suspend/resume, sorted event enqueue, finite/wrapped/indefinite TCB blocking, queue unlock and priority inheritance without injected mutex/wait/timeout returns. Prepared tick/list state remains synthetic. Each stops at PendSV-request entry, before exception delivery/task restoration; post-wake retry, cancellation and drain remain open. Owner effective priority8→24 and current task event-list membership compare exactly.

Normal integrated receipt already records original4166aa/416710, plain take41a24e and owner claim418d90. Recursive take/give and inheritance/timeout helpers are tested by the direct and blocking-boundary suites, not reached by those normal cases. Do not present all kernel paths as integrated runtime coverage.
