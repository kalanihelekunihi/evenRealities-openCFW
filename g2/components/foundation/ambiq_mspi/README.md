# Source-backed Apollo MSPI interrupt foundation

This component reuses six unchanged function texts from public Ambiq HAL
commit `5efc0228528a8adce5eae0d226fac85d2551eb3b`, Apollo510 SDK5.1.0 replay,
with the original BSD-3-Clause copyright/conditions/disclaimer preserved.
`SOURCE_PROVENANCE.json` records full source file and Git blob identities and
individual excerpt hashes. The selected source is
[am_hal_mspi.c at the exact commit](https://github.com/AmbiqMicro/ambiqhal_ambiq/blob/5efc0228528a8adce5eae0d226fac85d2551eb3b/mcu/apollo510/hal/mcu/am_hal_mspi.c).
The public replay is not proof of the unavailable private producing checkout.

The compatibility header represents the initial handle prefix/module, the
interrupt/XIP register window, and a sparse stock lifecycle state view with
opaque padding. It is not a full semantic HAL state
layout, initializer, DMA engine, clock manager or ISR. Module0..2 map to
0x40060000/0x40061000/0x40062000, stride0x1000. Prefix bits0:23 are magic
0xbebebe and bit24 is initialized; output pointer and module range are caller
preconditions, as upstream does not validate them. Caller serializes INTEN
read-modify-write and handle/configuration against concurrent writers.

| Original function | Runtime range | Register behavior |
|---|---|---|
| interrupt_enable | 0x4c2328..0x4c235c | read INTEN+0x200, write old OR mask |
| interrupt_disable | 0x4c235c..0x4c2392 | read INTEN+0x200, write old AND NOT mask |
| interrupt_status_get | 0x4c2392..0x4c23de | read INTSTAT+0x204; optionally read INTEN then return intersection |
| interrupt_clear | 0x4c23de..0x4c240e | write INTCLR+0x208, then volatile-read INTSTAT |

Invalid readable handle prefixes and NULL handles return2 before MMIO; valid
ones return0. The clear helper's read after the write must be retained. The
source establishes access ordering, not hardware write completion timing.
The simulator supplies an explicit synthetic W1C stimulus; the ordinary host
fixture deliberately behaves as RAM, so its INTSTAT does not auto-clear.

## Build and validation

From `g2/`, `make ambiq-mspi-simulator` compiles the selected C plus callable
entries for Cortex-M55/Thumb, soft-float, and links a standalone ELF at
0x10000 with RAM at0x20000000. It has no reset vectors or board startup and
changes no production provider. `make foundation-test` includes host and
compile/link tests; `CORE_TESTS` includes `test_ambiq_mspi`.

Use `make ambiq-mspi-simulator-test SCB_SIM_PYTHON=<Unicorn-enabled-python>
AMBIQ_SIM_REPORT=<new-report-path>` to execute the original/source comparison.
Output creation is exclusive and optimized Python is rejected. The shared
ELF loader bounds memory/table/segment sizes and records its own hash. Each
executed original instruction is checked against authenticated payload bytes.
Both bodies run without original callee stubs.

Final evidence: `g2/build/foundation/ambiq-mspi-simulator/comparison-heldout.json`.
68 cases cover all3 modules, OR/AND masks including all bits and the actual
NOR caller's0x1a80, raw/enabled-only status, zero state, invalid magic/init/NULL
handles and ignored high prefix flags. Return codes, complete output guards,
unchanged handles/registers outside intended effects, exact32-bit MMIO access
order and values are checked. Four source/host/build/verifier tests pass.

## Consumers and limits

Authenticated static callsites in the NOR service wrapper0x46f4ea and display
driver leaf0x592658 perform status(raw), clear(status), then service(status).
The NOR async write path0x59ce1e clears then enables0x1a80 (DERR/CQUPD/CQERR/
SCRERR). These callsites support transport use, not NVIC wiring or lifecycle
quiescence. See `g2/analysis/ambiq-mspi-cycle-2026-10-05/REPORT.md`.

No physical clock/power/IRQ/DMA/NOR/display transactions or concurrent RMW
were validated. There is no full driver, bootable firmware or byte-identical
source build claim. Authenticated source correspondence is distinct from
exact compiled-byte attribution; the latter adds0 bytes in this cycle.

## Lifecycle and recovered state layout

`ambiq_mspi_lifecycle.c` reuses the exact pinned `am_hal_mspi_disable` and
`am_hal_mspi_deinitialize` function texts (BSD-3-Clause), with the same retained
notice. The public SDK's complete state layout differs from stock: this
compatibility view uses independently observed stock offsets, never the public
struct as a drop-in. Proven fields are pTCB address slot+0x18, CQ pending count
+0x20, HP pending count+0x840, and XIP delay argument+0x8cc. Opaque bytes remain
uninterpreted. This subset tests the32-bit TCB slot only for nonzero; it does
not dereference that address or construct the full private state.

Disable validates the handle. Already-disabled returns0 immediately, including
when synthetic pending counts remain nonzero. When enabled, pending CQ or HP
work returns3 before any teardown. A nonzero TCB slot selects external CQ
disable, whose failure is propagated; CQ term is called only on success. The
enable bit is then cleared. DEV0XIP+0x90 bit0 selects a delay call with the
handle's+0x8cc argument. Deinitialize intentionally preserves stock/upstream
behavior: it ignores disable's result, clears init/module and returns0. This
return cannot be treated as proof of quiescence or permission to reclaim
queue/buffer storage. Actual stock cleanup callers are initialization failure
paths; no busy/error hazard manifestation on hardware is claimed.

`mspi_cq_disable`, `mspi_cq_term` and `am_hal_delay_us` are external provider
contracts required to link the lifecycle source. `simulator/lifecycle_seams.c`
supplies explicitly synthetic providers that log arguments/order and configured
status. They do not drain/free a queue or implement elapsed-time delay.

`make ambiq-mspi-lifecycle-test` uses `AMBIQ_LIFECYCLE_REPORT` (separate from
interrupt evidence). Final evidence is
`g2/build/foundation/ambiq-mspi-lifecycle-final/lifecycle-comparison-reviewed.json`:
102 cases execute both original lifecycle bodies, including the original
disable call from deinitialize. Only the three named external providers are
stubbed. Cases check exact prefix/module32-bit stores, preserved opaque bytes,
call order/arguments, status propagation, pending count paths, all3 modules,
XIP bit0, zero/max delay arguments, and invalid handles. These prove serialized
state transformations and call boundaries, not real queue drain or hardware
shutdown. The same final ELF also passes all68 interrupt comparisons.

See `g2/analysis/ambiq-mspi-lifecycle-2026-10-05/REPORT.md` for consumer evidence,
state offsets, original hashes, independent review and nonoverlapping delta.

## Bounded CMDQ provider profile

`make ambiq-cmdq-simulator` links actual CMDQ disable, termination, index refresh,
and local/global MSPI wrappers from `ambiq_cmdq.c`. `ambiq_cmdq.h` is an ARM32
stock-layout contract. `make ambiq-cmdq-simulator-test SCB_SIM_PYTHON=<Unicorn Python>`
runs the original/source comparison and creates its report exclusively.
The older `ambiq-mspi-simulator` retains synthetic CQ providers for its existing
fixture suite. This separation makes the provider choice explicit.

The real-CMDQ profile still supplies synthetic critical-enter and delay seams;
it is callable offline source, not a production interrupt-safe driver. Forced
termination refreshes indices, bypasses the busy-index test, clears init/CQEN/
pause-mask controls, and clears the global queue slot. It does not wait or free.
Disable uses caller-local +0x828; termination uses global module state. No buffer
allocation, valid-handle initialization, concurrency or hardware timing contract
is supplied. See `g2/analysis/ambiq-cmdq-disable-2026-10-05/REPORT.md`.

## Architectural interrupt-mask profile

`make ambiq-critical-simulator` selects the real PRIMASK provider; its default
output directory differs from the synthetic-critical CMDQ profile. Profile flags
are recorded, and this small callable profile always rebuilds, so switching
profiles in one directory cannot retain a stale ELF. `verify_cmdq.py --real-critical` executes the original and compiled
MRS/CPSID/BX instructions, initializes prior PRIMASK to0 or1, checks protected
index/address reads occur masked, and checks restoration. The compiled leaf is
exactly the original8 bytes. Upstream source/alias provenance is in
`INTERRUPT_MASK_PROVENANCE.json`.

Privileged execution is a precondition. This proves an architectural instruction
contract in serialized offline emulation; it does not prove pending-interrupt
delivery, scheduler/concurrency behavior, unprivileged enforcement or physical
wall-clock delay. Only delay remains intercepted in this profile. The separate
synthetic-critical profile retains its explicit provider limits.
