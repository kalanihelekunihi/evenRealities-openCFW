# Boot status, spot timer and data recheck

Current selected baseline remains `boot-coplacement-pow10-signed-round/receipt.json`: coherent bounded link, 374 units, 1,011 providers, three ROM imports. No selected Boot source changed in this round.

Four reachable source bodies were attributed to their selected implementations:

- Status poll `0x41d246`: current `status_poll.c` hash matches prior 496-case FIFO/poll stock/source receipt; native loop's selector, one MMIO read per iteration, delay(1) count and 0/4 result match.
- Spot timer initializer `0x41cc04`: direct full Thumb read/write order matches selected `startup_spot_timer.c`, including both writes to control, two all-ones compare registers and final OR bit.
- MSPI XIP-off minimum delay getter `0x424a18`: selected `device_configure.c` hash matches prior 2,823-case device-configure receipt whose native trace reaches this helper. Native frequency byte ranges and handle+0x8cc output match, with unmatched values untouched.
- Thread storage release `0x418ae8`: no retained decomp, so direct Thumb was used. Ownership 0 frees stack then TCB; 1 frees TCB; 2 returns; other values mask then fatal-store. Selected C preserves all three separate ownership reads.

The current [source-data check](boot-tail-data-pow10-round.json) compares 78 named semantic tail bytes in 11 selected ELF symbols to locked stock and passes. The audit accepts `--elf` and `--output` so future source snapshots can be checked without overwriting the old receipt. This is bounded data parity; compiler literal pools, final addresses, full scatter, and ROM-provided behavior remain separate.

Crosswalk `boot-body-crosswalk-status-spot-round.json` and reachability `boot-root-reachability-status-spot-round.json`: 654 reachable catalogue entries, zero machine-unattributed roots, 94 remaining rooted header-only proof leads, down from 98. These are proof leads, not a count of missing C bodies. Next native bodies include `0x419e22`, `0x419de2`, `0x419684` and `0x4223d8`.
