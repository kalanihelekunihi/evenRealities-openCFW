# File-close ownership through actual mutex and TLSF providers

**48 PASS original/independent wrapper comparisons**, executing actual static mutex creation/take/release, selected filesystem sync/unlink, and actual TLSF create/malloc/free/reallocation. [Independent wrapper](../../components/audio/file_close_offline/close.c), [results](results.json), [provenance](provenance.json), [instructions](original-disassembly.txt). No child result stubs or media operations.

## Recovered sequence and ownership

Original `file_close` `0x4745F4` loads file mutex from `0x200748F4` and acquires it with **1000 tick units**. Rejection returns-1 before touching the stream. Success calls backend `0x4CFAD0(stream[0], stream+4)`, retains its status, releases file mutex, and calls wrapper-free `0x474D16(stream)`. It normalizes backend status to0 for nonnegative or-1 for negative **after attempting wrapper release**. Backend failure does not branch around that release in source; negative backend status was not injected/tested here.

Backend asserts file is on filesystem open-file list at fs+0x28, then `0x4CDCE4` syncs via `0x4CDF74`, unlinks via `0x4CB0A0`, and conditionally frees file cache buffer when config+0 is NULL. The test cache is explicitly caller-owned, so this optional buffer free is excluded. Both clean flags0 and already error-marked flags0x80000 close without block I/O in the selected original paths; the latter bypasses sync rather than introducing a synthetic negative status.

Wrapper-free acquires a **second mutex**, heap mutex `0x200748F8`, also with1000 ticks, then invokes real TLSF free `0x4D0808(*0x20074ABC, stream)` and releases that mutex. If heap-mutex acquisition rejects, it reaches error logger `0x4733EE` and later an assertion path. Tests stop before the logger first instruction, proving no TLSF free at that boundary; they do not manufacture logger/assertion returns.

| Phase | Wrapper ownership |
| --- | --- |
| File-mutex rejection/ISR rejection | Wrapper and open-file list retained |
| Successful backend close | File removed from open-file list before wrapper release |
| Heap-mutex rejection | File already unlinked, wrapper not freed at logger boundary |
| Successful heap release | Wrapper freed; actual malloc of same size returns its former address |

## Validation and boundaries

Fresh fixture allocates 100-byte stream through stock TLSF create-with-pool `0x4D06EC` and malloc `0x4D0722` in a 64KiB synthetic arena. Both file/heap mutex queues are initialized through actual static mutex provider `0x4416F0`, regular or recursive. Synthetic current TCB has unchanged equal base/effective priority and empty waiters; taskcount0/running1 is fixture scaffolding, not a reachable scheduler-state claim. Cases vary recursive tagging, two clean/error flags, head/second list placement, thread/null-file-mutex/ISR context, and valid/null heap mutex. They compare used ABI call arguments, result or boundary, complete arena hash, mutex/TCB bytes, list links and actual wrapper address reuse. Original and independent wrapper share the original filesystem/heap providers; this is not an independent entire filesystem or TLSF reconstruction.

The caller's recording-close state and dirty file/cache need mounted filesystem state and block data to continue actual sync/media behavior. No dirty-flush success/failure, pending mutex waiter/timeout, storage callback, hardware, live scheduling or callback concurrency is modeled. These selected software ownership facts advance teardown analysis without establishing complete recording shutdown or safe patch design.
