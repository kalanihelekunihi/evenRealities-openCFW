# Bootloader rooted body and GPIO PRIMASK round

## Actual selected-source correction

Stock Thumb body `0x41df48..0x41dfc5` reads GPIO enabled/status registers under saved PRIMASK, then executes unconditional `msr PRIMASK,r0` at `0x41dfbc`. Its child `0x41b8ec` returns old PRIMASK and disables IRQs. Selected `initializer_callbacks/gpio_irq_runtime.c` had restored PRIMASK only under an IPSR/CONTROL predicate. The selected C now restores saved PRIMASK unconditionally, preserving the stock register read and return order. This correction is supported by full native disassembly, not inferred from HAL intent.

`boot-gpio-status-current-oracle.json` passes 32 bounded original/current selected ELF cases across invalid/boundary GPIO numbers, enabled/disabled masks, and initial PRIMASK 0/1. All 126 catalogue bytes in `0x41df48..0x41dfc5` were visited. Synthetic MMIO and explicit special-register instruction cuts limit this to CPU-state/source behavior; no physical interrupt claim. The coherent candidate at `boot-coplacement-gpio-primask-round/receipt.json` is `PASS_BOUNDED_LINK`, 374 selected units, 1,011 providers, three genuine ROM imports, 34 callback relocations, 158,820 image bytes. All source hashes matched its receipt after build. Stock length is a comparison, not an established partition capacity.

## Full-body source attribution

- `0x418148..0x4181d7` scheduler bootstrap: selected `thread_creation/scheduler_bootstrap.c` passes four bounded original/current C cases in `boot-scheduler-bootstrap-oracle.json`, visiting 130/144 bytes. The remaining 14 bytes are the unexecuted fatal branch. A proposed unconditional port-start change failed the oracle and was reverted; native ordinary failure skips port-start. The selected source hash equals the prior coherent receipt.
- `0x417fe4..0x41806d` task-state classifier: native disassembly and five literal anchors match selected `thread_termination.c`, including null fatal, current task, delayed/overflow, suspended list, deleted list, and one-byte state check at TCB+0x6c.
- `0x41a4a6..0x41a52b` queue copy-in: native disassembly matches selected `queue_send.c` for zero-item release, forward and reverse cursors, wrapping, mode-2 overwrite count, and release return.
- `0x418922..0x4189a1` timeout check: native disassembly and tick/overflow literals match selected `queue_receive.c` for null fatal, infinite timeout, overflow history, remaining-tick update and recapture.
- `0x417d16..0x417d93` dynamic task creation: native disassembly matches selected `kernel_dynamic.c` for 16-bit stack-word truncation, two allocations, 112-byte TCB clear, ownership, child initializer, registration and failure return.
- `0x41d92c..0x41d9a9` power register update: native disassembly matches selected `clock_class_providers.c` through bounds, two table gates, value bitfields, latch/register write order and PRIMASK restoration. Both seven-word source tables were extracted from stock at `0x433460` and `0x43347c` and matched exactly.

The five bindings outside scheduler and GPIO are structural full-body matches without new runtime oracles. The GPIO body has the 32-case source oracle. None of these bindings is evidence of complete image layout, callback runtime behavior, or hardware IRQ delivery.

## Open gates

The rooted crosswalk is a proof backlog, not a missing-body count. The latest `boot-body-crosswalk-dynamic-power-round.json` and `boot-root-reachability-dynamic-power-round.json` audit found 123 header-only leads among 654 reachable catalogue entries and zero machine-unattributed roots. Three genuine ROM imports, callback/runtime semantics, remaining selected-body proof leads, and final data/scatter/image equality remain open. The next largest lead is MSPI clockgen control `0x4249a0` (120 catalogue bytes).

## MSPI clockgen follow-on

Stock `0x4249a0..0x424a17` exposed a selected-source MMIO read-order error: for enable=true and configure=false, native reads `0x40004110` once before the set-bit write; prior C read it once before the branch and again at the set-bit operation. `nor_mspi_power/mspi_clockgen_control.c` now reads in each native path, preserving configured two-read/two-write behavior and disable one-read/one-write behavior. An intermediate attempt to change the return and shift arithmetic failed bounded original/current comparisons and was reverted. The native epilogue returns the old PRIMASK because it overwrites its saved R3 slot, and ARM register shifts use the low eight bits of the count; final C expresses both facts.

`boot-mspi-clockgen-current-oracle.json` passes 36 combinations, visiting all 120 native bytes and comparing ordered MMIO read/write/delay events, final register, return and PRIMASK under explicit CPU/delay cuts. `boot-coplacement-mspi-clockgen-ordered-round/receipt.json` is coherent `PASS_BOUNDED_LINK`, 374 units, 1,011 providers, three ROM imports, 34 callback relocations and 158,820 image bytes; all selected source hashes match the receipt. Synthetic MMIO is not hardware clock proof. The fresh `boot-root-reachability-mspi-clockgen-round.json` audit reduces rooted header-only proof leads to 122 of 654, with zero machine-unattributed roots. The next largest lead is `0x419186` (118 catalogue bytes).

## RTOS task block follow-on

The complete stock `0x419186..0x4191fb` Thumb body and six literal SRAM anchors match selected `thread_creation/timer_wait.c` `opencfw_boot_task_block`: event-list unlink, indefinite suspended-list append, tick-wrap routing to overflow/normal delayed lists, sorted insertion and next-unblock update. The native saved R3 return is ignored by its typed void callers. This is structural body attribution, not a fresh tick/IRQ runtime oracle. `boot-body-crosswalk-task-block-round.json` and `boot-root-reachability-task-block-round.json` now count 121 rooted header-only proof leads of 654 reachable catalogue entries, zero machine-unattributed roots. The next largest lead is GPIO callback service `0x41e09a` (116 catalogue bytes).
