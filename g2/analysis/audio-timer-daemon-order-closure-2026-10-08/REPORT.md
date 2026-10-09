# Actual timer-daemon command-versus-expiry ordering

Five reconstructed native functions pass **40 original-instruction daemon-order cases plus22 next-expiry/time-sample cases**, on one final ELF `6e28bd25c7f6d8123e0a8a1f55fb679a44272c0d14be21808fbf6145d13525f9`. [Readable C](../../components/audio/timer_daemon_order_offline/daemon.c), [interface](../../components/audio/timer_daemon_order_offline/daemon.h), [pseudocode](pseudocode.md), [exact validation](exact-build-validation.json), [addresses/code hashes](function-bindings.json). Actual original kernel/queue/allocator/list/tick/wrap/reload/adapter providers remain explicit, not result stubs. This is a stronger control-order batch, not a completely native kernel or byte-identical firmware.

## What the real daemon selects

Stock task body **0x47E878**, only20 bytes, loops:next expiry0x47E8F2 → process-or-block0x47E88C → drain commands0x47E97A. It does **not** check/drain the command queue before a due timer. Process-or-block suspends scheduler, samples tick and switches lists on detected wrap. With no wrap,nonempty active list andnow>=expiry, it resumes scheduler and processes expired timer0x47E83A. Only after that callback returns can the task reach command drain.

A coherent queue containing stop3/delete5 does not alter this ordering. The tests use actual publisher commands and real queue initialization/copy, then enter the actual daemon task body; they do not manually choose an expiry helper versus command helper as separate phases. At ticks150/151 with expiry150,original/native execution reaches the real user callback entry while queue count remains1 and command drain has not run. At tick149,restricted queue wait finds the queued command through actual original code,then command drain unlinks/stops or deletes the timer; the next-iteration boundary has queue count0 and active list count0.

## Auxiliary lifetime: stronger conditional reachability

For actual CMSIS delete0x44953E with dynamic auxiliary ownership,successful publication frees the8-byte callback payload (24-byte minimum allocation) immediately. Timer.ID and active list still reference it until daemon processing. In the due-at-daemon-entry fixtures,real daemon now chooses expiry first and reaches adapter0x449398 → user entry0x53C2A4 using that old auxiliary. **This is a demonstrated instruction path through the actual daemon selection**, improving the earlier separate-phase evidence.

Two cases reuse the freed payload using actualmalloc(8),which returns the same address,replace the argument with0xCAFEBABE,then enter real daemon. It reaches user callback entry with0xCAFEBABE while delete remains queued. No user callback instruction is executed; no synthetic successful callback return is supplied. Static/dynamic timer allocation and auxiliary allocation flags remain separate. Selected autoreload cases reinsert timer before callback and still leave queued delete pending.

These are constructed coherent timer/queue/heap states,not an observed device failure. Entering the daemon task directly is not proof a live scheduler reaches that state at a particular time. IRQ/preemption,ready/blockedTCBs,actual caller priorities and callback bodies remain unverified. Do not promote this to a hardware use-after-free claim or safe patch design. It does prove that enqueue success alone is not callback quiescence andthat queued deletion is not itself a callback-generation/ownership check.

## Wrapped ticks and blocking boundary

Selected wrap cases start with last tickUINT32_MAX,new tick0,current list empty andtimer in overflow list. Real wrap helper swaps lists; process-or-block skips ordinary expiry because lists switched,then drain processes pending stop/delete before the next iteration. Twenty-two leaf cases compare empty/nonempty next-expiry reads andall selected now/last relations with empty-list switching through actual original tick/wrap providers. No live overflow timing is inferred.

Two empty-command-queue cases stop **before first instruction0x442030** of restricted queue wait,with actual queue/tick/indefinite arguments captured. Advancing these blocking cases faithfully requires the daemon’s currentTCB,ready/delayed/pending-ready lists,scheduler state andexception/context-switch execution. This fixture has modeledtaskcount0/running1 anddoes not invent a task wake or blocked-call return. Callback bodies likewise stop at actual first user instruction. Next-iteration stops occur only after real completed command drain; the infinite task is not falsely reported as returned.

## Source and practical implication

Existing preserved FreeRTOS V10.5.1 pin `def7d2df2b0506d3d249334974f51e427c17a41c` supplies the corresponding control algorithms. Actual Apollo instructions/field offsets govern the native implementation; no unique kernel release/config attribution is claimed. Timers retain44-byte prefix,16-byte queued command andstatus bits active1/static2/autoreload4; opaque+0x24 meaning is still deliberately unassigned.

App/CFW shutdown/cancellation must distinguish command accepted,command consumed andcallback complete. For a cancellation-safety conclusion,the missing input is a coherent live scheduler/daemon/callback trace (TCB identity,priority,ticks,queue state andallocation/reuse events),or a validated fuller kernel/exception fixture—not another source-inventory scan. No cancellation/memory patch is implemented.

All previous seals,110 inputs,four checkpoints andstaging are preserved. No commits,production/shared-gate edits ordevice writes. [Preservation](preservation.json). Other source leads remain available; this does not assert global source exhaustion.
