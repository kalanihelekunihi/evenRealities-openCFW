# NOR flash mutex and power-guard review

REA/Ghidra 12.1.4 inspected seven functions in the locked Apollo main image:
sleep 0x46F50C (32 B), wake 0x46F52C (26 B), mutex initialization 0x46F546
(96 B), mutex lock/unlock 0x46F5A6/0x46F604 (94/90 B), and flash guards
0x46F65E/0x46F674 (22 B each). These are bounded observations, not
independent pseudocode admission or a workflow gate.

## Shared-handle loads

The native mutex wrappers load the handle at 0x20074548 for the NULL check
and load it again for `osMutexAcquire` or `osMutexRelease`. Native
initialization also reloads that cell after publishing the result of
`osMutexNew`. The C compiler previously merged those reads because the
shared pointer object was not volatile. A controlled cell change can
therefore change the native helper argument or failure branch while the
old C uses a cached value.

The pointer object's definition and all declarations now consistently use
`void * volatile`, preserving those reads. This does not add synchronization
or claim thread safety. It preserves observed machine memory effects.

The address distinction is important: **0x20074548 holds the handle**;
**0x20072A88 is its 0x50-byte static control-block storage**. The mutex
attributes at ROM 0x785CF0 point at that storage. The device handle is at
0x20074544; mode and sleep-state bytes are at 0x20074FB8/FB9.

## Existing policy preserved

The outer lock calls the mutex wrapper, then wakes MSPI and clears the sleep
byte when mode is not 1. The outer unlock requests sleep only when mode is
not 1 and sleep state is not already 1, then releases the mutex. Existing
behavior continues after RTOS lock/release errors and ignores the power
helper's return status; this review does not invent different error policy.

Two forwarding-only files duplicated the flash-guard identities. They were
removed. The NOR caller aliases still point at `audio_uart_ring_config_lock`
and `audio_uart_ring_config_unlock`; the font-resource caller aliases now
point directly at those same bodies. No extra implementation or source-plan
selection was added.

## Execution evidence

All **1,232 guard cases** and **34 mutex-initialization cases** now agree
with stock. Comparisons include ordered handle reads, sleep-state writes,
RTOS/power helper arguments and order, and log string contents. The guard
grid covers mode/sleep values 0, 1 and 2; NULL/non-NULL mutexes; successful
and failed RTOS/power calls; all eight log flags; and controlled mutations
between reads or calls. Initialization covers existing/new/failed mutex
creation and a cell change after publishing the constructor result.

Before the repair, only 608/1,232 guard cases and 16/34 initialization cases
matched when memory-read traces were included. Stable-handle cases could
pass identical arguments while still missing the second read. Explicit
mutation cases additionally demonstrate stale helper arguments or a stale
post-publication failure decision.

RTOS, power and logging helpers were controlled mocks. These checks do not
prove their implementations, physical XIP behavior, peripheral timing,
interrupt concurrency, original-compiler code generation or byte identity.
Raw REA observations and result summaries are in
[`norflash-guard-review.json`](../../evidence/norflash-guard-review.json);
wrappers, original snapshots and per-case traces are under
`build/goal-flash-guard/`.
