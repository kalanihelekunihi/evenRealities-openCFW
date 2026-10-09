# UART retained power/configuration

**265 original-instruction versus native-source comparisons PASS** against final ELF `64135f5d52c67c77cc80bbe6421d9fbe2b107ac988dfb1b3893cbcdd920b3d7a`. Four selected SDK function texts remain unchanged, with explicit sparse ABI/register adapters and quotient-only division support. [Results](results.json), [exact receipt](reproduction-receipt.json), [readable pseudocode](pseudocode.md), [source](../../components/audio/uart_power_config_offline/README.md).

Retained sleep saves eight registers; retained wake rejects invalid saved state before provider calls. Sleep clears interrupts and CR before peripheral disable. Requested normal/deep sleep use the same tested wrapper flow. Provider return errors do not propagate through these wrappers. Configuration rejects SYSPLL on revision0x21 after clearing CR and setting CLKEN, and baud errors return after clock acquisition without wrapper rollback. None proves physical power/clock state.

The baud helper is actual0x58DE38, called by configure0x58E09E. Its integer reported rate differs from requested rate: HFRC921600→923076; requested1500001→1548387 after48MHz selection. The threshold is strictly greater than1500000; revision>0x21 enables gate updates. Do not interpret reported metadata as measured bitrate.

Validation includes modules0/1/3, retained/nonretained states, invalid saved state, chip revisions0x21/0x22, HFRC/SYSPLL/invalid clock selections, fractional divisors, parity/data/stop/flow/FIFO fields, invalid handles for power/configure and explicitly synthesized provider statuses0/7. Original instructions are stepped unchanged; native reached addresses guarded. MMIO backing and provider returns are synthetic. Zero/overflow denominators, real scheduling, power timing and full runtime ABI are not established.

**Important source limit:** the pinned interrupt-clear body adds a volatile MIS read absent from stock and may dereference a NULL handle before validation. The fixtures compare final state/return for mapped valid handles; this is not exact read-side-effect equivalence or NULL safety. Quotient support does not supply remainder registers and is not a complete __aeabi_uldivmod implementation. These limitations are retained rather than presented as complete source closure.

## RX ownership recap and concrete remaining providers

The completed [RX batch](../audio-uart-rx-stream-ownership-2026-10-09/REPORT.md) has582 passing cases. Channel1 flush invokes0x5415E6, copies a prefix into2048usable stream bytes, ignores accepted count, then resets staging. Synthetic pressure shows rejected suffix is not retained; no hardware loss claim. Stream receive0x57E136 and notifier0x455DC0 remain concrete receiver/task-copy dependencies.

Clock request0x4C44BC/release0x4C4530 already have [source-backed dispatch/ownership](../audio-clock-public-dispatch-closure-2026-10-08/REPORT.md); their documented synthetic readiness and runtime dependencies remain, so they were not reinvented here. Peripheral enable0x47F5B8/disable0x47F7AE lead to the [descriptor provider](../power-domain-descriptor-2026-10-06/REPORT.md); full powered-operation providers still need bounded tracing/composition. Channel3 routing and IRQ drain remain distinct from the logger's unqueued channel1. Shared-formatter reentrancy remains unproven without actual call/preemption evidence. Source leads are not exhausted.

No commits, production/device/shared-state edits. Prior2704 seals,110inputs,fourcheckpoints and staging verified unchanged in preservation.json. This is bounded offline validation, not independent review, whole-firmware/source completeness or byte equality.
