# Generic queues and CMSIS source closure

New source recovers task send/receive and their two private copy bodies, three CMSIS scheduler/context/put providers, and five timeout/suspend/event/next-unblock providers. Public generic queue bodies are selected from the preserved FreeRTOS 10.5.1 queue source (def7d2df2b0506d3d249334974f51e427c17a41c). CMSIS wrappers and stock helper differences are reconstructed, not attributed as pristine public source. Independent byte-loop copy supports nonoverlapping valid buffers, not full libc attribution.

## Behavior

CMSIS queue-put ignores priority. IPSR, or active-scheduler PRIMASK/BASEPRI, selects ISR-style submission; before scheduler start masks alone do not. ISR submission rejects nonzero timeout with -4, reports full as -3, and requests PendSV only when a strictly higher-priority receiver wakes. Task submission reports invalid arguments -4, no-wait full -3; -2 is the static positive-timeout failure mapping, not an exercised resumed timeout completion. Scheduler suspension without masks does not itself select ISR routing.

Queue ownership copies item-size bytes into queue storage synchronously on successful send. Receive copies out and updates queue cursors. Front/back and length-one overwrite are modeled; zero-size overwrite misuse can increase count beyond capacity and is not a supported semaphore contract. Main-image FromISR lock increments are task-count capped; do not apply earlier case-image uncapped behavior here.

Timeout state is two uint32 fields: overflow counter and entry tick. UINT32_MAX waits do not expire. Finite checks use unsigned elapsed ticks, with overflow-counter/entry comparison detecting expiration. Event placement inserts current TCB event item (+24) into sorted waiters and then delayed/suspended task state. Units are scheduler ticks; no millisecond conversion is established.

## Validation and boundary

Exact final ELF and inputs are authenticated in exact-build-validation.json. **1,345 queue/context/composition comparisons +504 timeout-provider comparisons PASS**. These are not 1,849 unique new functions. Suites reuse sealed FromISR, wake/list/critical, delayed-block, scheduler-resume and tick providers. All reached native instructions stay in the native region, except explicit entry cuts before port yield or mutex disinherit. Positive waits establish actual blocking state up to yield, not task resumption, exception return, completed timeout or full mutex inheritance.

Continuous Unicorn 2.1.4 carries anomalous Thumb IT state across stock memcpy return for a receive fixture. Unmodified original instructions run one-at-a-time agree with native code; continuous execution writes beyond payload. engine-discrepancy.json records this limitation. No opcode, flag or helper result was substituted. This is not evidence of a hardware firmware defect.

## Use and remaining leads

Reusable source and ABI: [queue.h](../../components/audio/queue_cmsis_offline/queue.h), [compat.h](../../components/audio/queue_cmsis_offline/compat.h), queue.c/cmsis.c/blocking.c. Blocking completion requires real exception/task scheduling state or a validated scheduler emulator; mutex release needs priority-disinherit body and coherent ownership fixtures. These are bounded offline helpers, not production firmware, independent review, whole-image source closure or byte equality.
