# Boot rooted header-binding round

Locked stock SHA-256: `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

The selected archive remains the `boot-coplacement-kernel-noop-round` snapshot: 371 source units, 1,008 defined providers, three genuine ROM imports. This round changes attribution evidence only; it does not claim a newly compiled C body or full image equality.

## Completed source groups

Nine largest header-only native entries now have explicit selected provider bindings in `manual_body_bindings.json`. The binding audit enforces that each named symbol is defined by the stated selected source unit. They cover:

- MSPI control 0x4251c0: full request discriminator 0..40 split across selected `control_read.c`, `control_remaining.c`, and request-specific selected lowers. Native fourth decompiler argument is only an output slot passed to CMDQ allocation after saving; the entry value is not a required fourth input.
- IAR formatter 0x41e47a: selected ARM word-cursor entry and parser/render/callback sources. Previous bounded formatter oracle exists; secure abort and untested grammar remain separate runtime gates.
- MSPI private/public device configuration 0x424120/0x424be4 and power control 0x426808: selected mode table, register sequences, public adapter and power-control body.
- SYSCTRL deep sleep 0x41a71e: selected WFI and wake control-flow body, with physical power/wake behavior still unqualified.
- Startup clockmux 0x41acb2 and power root 0x41c4b4: selected ambient-register Thumb entries and C cores, not raw decompiler signatures.
- Registered Spot power callback 0x42ba00: selected callback is written by startup runtime slot producer.

The previous crosswalk gave an unreviewed header lead precedence over an already reviewed manual binding. The audit now reports reviewed manual evidence first, while still requiring selected source and provider agreement. It moved 36 labels from header-only to reviewed manual: 27 existing bindings previously hidden plus these nine new checks. A further selected SPOT power-state callback 0x42a878 has an explicit binding to its source and tested FP helper closure. The whole catalogue now has 286 header-only labels (from 323); among 654 conservative vector/scatter direct-call reachable labels, 188 remain header-only (from 215). The two reachable comment-only leads were then bound to selected EasyLogger port wrappers `elog_port_get_p_info` and `elog_port_get_t_info`; both call the same selected static `thread_name` helper as native 0x41a6f0 and 0x41a6f8. Zero comment-only leads remain in the conservative direct-root graph. These are proof backlog counts, not missing-body counts. The 654 graph excludes indirect/runtime-installed roots.

No original-byte runtime comparison was added for this subgroup. Source ownership and selected provider existence are established; semantic equality remains scoped to the individual prior receipts and future tests. The three ROM imports, final scatter/layout, GC/indirect root closure, and hardware runtime remain open.
