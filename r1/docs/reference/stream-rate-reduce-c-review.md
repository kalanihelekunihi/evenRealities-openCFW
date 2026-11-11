# R1 stream rate reduction in C

`r1/src/application/runtime/native_stream_rate_reduce.c` supplies native entry
`0x8a068` (214 contiguous instruction bytes). It resolves cleanup's surviving-list
rate-reduction import. [The machine-readable review](stream-rate-reduce-c-review.json)
retains source/build hashes, REA assembly and byte receipts, replay evidence,
negative controls and the remaining SDK return boundary.

## Recovered behavior

The reducer returns zero for a null object or a zero maximum rate. It scans every
listener's rate byte, including marked listeners, and returns the current object
rate without further work when that rate is already at or below the maximum.

When reduction is needed, a nonzero buffer triggers allocation of twice the
maximum rate times sample width. Width, buffer, used count and old rate are
reloaded after allocation. The existing sample converter supplies the resized
buffer and copied count. The buffer pointer is read again before free, so a
provider mutation can change which allocation is released. Only afterward are
the new buffer and copied count installed. Allocation failure enters the existing
architectural fault adapter. A zero old buffer skips allocation and conversion
but still changes the rate and timer.

The captured nonzero maximum determines the new period. Rate is stored before
loading the timer pointer and calling the existing C period setter. Logging mode
is sampled with stock short-circuit ordering. Each selected diagnostic reloads
the current rate, including after provider changes. A zero rate uses the existing
unresolved `r1_stream_zero_divisor_result` boundary instead of undefined C
division. The no-SDK-log return reproduces stock's `LSLS R0, R0, #30`, returning
the shifted mode word rather than the original mode.

## Explicit raw SDK result boundary

Stock's SDK diagnostic tail enters `0x799d6`, passing tag `0x001c0003`, the format,
object and period. Its sixteen-byte wrapper calls `0x90fec` and leaves the resulting
R0 un-restored. The current cleanup adapter forwards that register result.

The already linked SDK `nrf_log_frontend_std_2` has a `void` C return type, verified
in its source. Calling it as an integer-returning C function would use an
incompatible function type; calling it normally would not promise the stock R0
value. This candidate therefore exposes `r1_stream_rate_reduce_log_tail_result`
with the stock arguments and integer result. It remains unresolved. The existing
SDK provider was not duplicated, retyped or replaced, and this boundary is not
claimed as a completed C implementation. Its native bytes and SDK source hash are
recorded in the JSON review. This preserves the tested raw-result contract while
leaving the remaining ABI work visible.

## Verification

The primary fixture passes 2,367 paired native/C cases, comparing calls, arguments,
returns, final object/list/timer state and ordered watched reads/writes. It
executes the actual C timer-period setter. Cases include empty/zero-rate lists,
maximum selection, rates through 255, widths through 65,535, missing buffers,
allocation failure, null timers, logging combinations, zero-rate changes during
logging and 256 seeded provider-mutation sequences. Raw result comparisons cover
no-op branches, shifted mode returns and modeled SDK tail results. List,
allocation, sample conversion, free, logging and zero-divisor providers are
modeled in that fixture. Caller-saved registers are deliberately clobbered at
modeled calls.

Another 320 paired cases execute the actual native/C list head/next, sample
converter and period setter, with memory moves modeled. Another 768 execute the
actual cleanup/stop, rate reducer, list head/next/empty, converter and period setter
together. The latter models unlink and timer release and poisons freed listener
records. Both integration fixtures compare calls, arguments, return values and
final state. Their memory observers are disabled for the previously documented
Unicorn list-head IT observer issue; ordered memory-access claims come from the
primary fixture. Linked provider hashes are recorded.

Six compiled negative controls are rejected: wrong maximum selection, wrong
rate store, freeing the stale buffer pointer, discarded copied count, unshifted
mode return and halved allocation size.

Ordinary reducer provider depths match at 32 bytes, and the SDK logging-result
tail is entered at zero bytes on both paths. The null timer setter retains its
known extra eight-byte C fault frame (40 bytes total versus native 32). Fault
comparison stops before BASEPRI/store gateway effects. Zero division is replayed
under Unicorn with DIV_0_TRP disabled, not proved on hardware. Return SP,
callee-saved registers and masks are checked on normal returns; private frames,
caller-clobbered registers and APSR are excluded. Full stack, exception and
instruction identity remain unproven.

## Build status

`make sources-check` passes. All 613 units compile (539 application and 74
bootloader); both relocatable compositions pass without failures or duplicate
strong symbols. All preceding 612 objects remain identical. Only the reducer
unit is added to the manifest, and only its supplemental entry is added to the
frontier. The rate-reduction import resolves and the raw logging-result boundary
becomes explicit, leaving 169 application and 34 bootloader imports.

Scoped qualification compiles the unit but admits zero bytes. The canonical
source plan is unchanged. The fresh hybrid matches locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
using 4,271 source-built bytes, 641,889 executable pull-through bytes and 248
resource bytes. This does not establish a complete source-only link, candidate
byte identity, real allocator/timer integration or physical sensor delivery.

Reports: `build/sources-goal-r1-stream-rate-reduce-final-c/report.json` and
`build/hybrid-goal-r1-stream-rate-reduce-c/build-report.json`. Experiments and
fixtures remain under `build/goal-r1-stream-rate-reduce-c/`; durable results are
retained in the JSON review above.

The architectural zero-divisor dependency is now supplied by the
[shared primitive](divide-zero-c-review.md), with these callers tested against
the actual provider under nontrapping emulator conditions.
