# Public native-task allocation ABI

R1's public FreeRTOS allocation declarations now match the recovered native
backend: opaque `StaticTask_t` storage is 112 bytes, aligned to four bytes,
and `configSTACK_DEPTH_TYPE` is 32 bits. Previously the configured upstream
opaque type was 92 bytes and dynamic stack depth was narrowed to 16 bits.

This is an allocation contract, not a claim that upstream's generic TCB fields
have native semantics. The R1-owned `FreeRTOS.h` wrapper retains the upstream
type separately as `R1UpstreamStaticTask_t`, then declares native opaque storage.
It includes the pinned upstream header by repository-relative path because
forced local contract headers can make include-next resolve back to the wrapper.
The existing native field layout remains in `native_task_construction.h`.
The generic upstream tasks.c candidate stays excluded from composition; its
TCB layout cannot be used interchangeably with the native backend.

The SDK profile's existing native-header include argument moves ahead of the
upstream FreeRTOS include argument, bringing its app-timer consumer under the
same declarations. All 42 FreeRTOS consumers in the complete build depend on
the wrapper. Manifest units and link eligibility are unchanged. Idle/timer
memory callback objects and their existing 112-byte-plus-256-word reservations
remain byte unchanged; their compile-time extent guard is now equality.

[Machine-readable evidence](task-public-abi-review.json) binds sources, compiler
probes, REA, executable API checks, object audit, source build and hybrid report
by SHA-256. The prechange compiler probe reports 92-byte public controls and a
two-byte depth type. The corrected probe accepts 112 bytes and four-byte depth.
REA confirms stock dynamic construction at 0x983b8, including its 112-byte TCB
allocation and full-word stack-depth handling. Native construction source and
its recovered field-offset assertions provide additional layout evidence.

Actual compiled before/after CMSIS `osThreadNew` executes in 196 cases (392
executions). The new object rejects static control sizes 92 through 111 that the
old object accepted, accepts sizes 112 and 128, and preserves dynamic depths
65536 and larger instead of truncating them to 16 bits. Zero/default stack size,
partial allocation descriptions and creation success/failure are checked.
Task-creation and scheduler-state seams are modeled; this is an API acceptance/
argument test, not a stock comparison of CMSIS or native construction execution.
Native/public constructor binding, actual memory allocation, physical startup
and scheduling remain unfinished. The unresolved constructor names are retained.

Only two objects differ from the previous full R1 build: the composed CMSIS
adapter (`osThreadNew`) and the excluded upstream tasks.c candidate. Every other
compiled object is byte unchanged, including native task, queue, scheduler,
mutex and static-memory providers. All 573 units compile without failures or
duplicate strong symbols. Import sets remain 181 application and 34 bootloader.
The canonical plan is unchanged at 3,857 source-built bytes, 642,303 executable
pull-through bytes and 248 resource bytes. The hybrid still equals the locked
application byte for byte. Source completeness, a complete source executable
link and hardware operation remain unproven; no G2 gate advances.
