# Boot queue and source ownership round

Locked stock bootloader SHA-256: `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.
Current selected candidate remains `boot-coplacement-stimer-ordered-round/receipt.json`: coherent bounded link, 374 selected units, 1,011 providers, three genuine ROM imports and 34 relocated callbacks. No selected source changed in this round.

## Completed bounded groups

- Queue unlock `0x41a556`: new stock/current C eight-case oracle, all 110 native body bytes visited. Signed transmit and receive locks, child order, queue/list state and yield calls match under controlled children. See `boot-queue-unlock-current-oracle.json`.
- IOM descriptor publisher `0x42c45a`: new stock/current C 18-case oracle, all 108 native body bytes visited. Seven ordered MMIO writes, ring record/handle state and rollover cases match synthetic RAM/MMIO. See `boot-iom-descriptor-publish-current-oracle.json`.
- Static queue constructor `0x419c9c`: current selected source hash equals prior 240-case stock/source receipt. Native control block checks, fifth argument truncation, owner marker and initializer call are bound; invalid fatal continuation was outside that receipt.
- IAR fill `0x41560c` and aligned copy `0x4156ac`: both selected in unit 071. Current source hash matches the prior Cortex-M55 QEMU 840-case stock/source receipt (504 fill, 336 copy). Final RAM/ABI proven for its tested nonoverlapping inputs; access order is not equivalent for fill.
- Main init `0x41b862`: selected source hash matches prior startup comparison receipt, and full native pseudocode order matches its 13 service calls, conditional error log, callback load and terminal spin. Installed callback value and fatal continuation remain external qualifications.
- RTOS heap initialize `0x4198a0` and insert `0x4198fa`: current selected source hash matches the 159-operation heap stock/source receipt comparing the full 81,920-byte arena and globals after each operation.
- PendSV entry `0x41b31c`: current selected named-ISA source hash matches the two-case FP PendSV stock/source receipt. Hardware exception delivery, return and lazy FP stacking are unqualified.

The final rooted crosswalk is `boot-body-crosswalk-nor-mspi-round.json` and `boot-root-reachability-nor-mspi-round.json`: 654 reachable catalogue entries, zero unattributed roots, 102 remaining rooted header-only proof leads, down from 118 at the preceding checkpoint. These 102 are proof leads, not 102 missing C bodies.

## Next finite source gates

- NOR JEDEC reader `0x42059e` was requalified below with the current source; its apparent two-register decompiler return is not a caller-consumed 64-bit ABI.
- Continue rooted full-body/current-source checks at `0x41cc48`, `0x423e40` and later native service bodies; review reachable callback/scatter ownership rather than treating name matches as full bodies.
- The three genuine ROM imports, installed callback values, complete scatter/data/layout and hardware startup/IRQ behavior remain separate image-completion gates.

## Continued NOR and control qualification

A fresh isolated build of the **current** selected `nor_init.c` passed six stock/source cases, 414 distinct original trace bytes across the NOR initializer, JEDEC reader and status transfer: `boot-nor-current-isolated/comparison.json`. Native disassembly shows `0x42059e` saves incoming R1 and restores it with `pop {r1,r2,r3,r4,r5,pc}`; this explains Ghidra's misleading 64-bit `CONCAT44` return. Its caller at `0x4204c4` immediately copies only R0 to R4, and current C's 32-bit status return matches that consumed contract. No selected source correction was warranted. MSPI/ROM/logging providers remain bounded fixtures.

The selected `platform_control/control.c` hash matches prior 496-case platform-control and 19-case application-storage receipts for `0x42e4a0`. The native and source order of alignment check, critical save, guard, MRAM call, guard exit and PRIMASK restore is bound; ROM `0x0200ff20` is a controlled lower in those receipts. The selected `kernel_runtime.c` hash also matches a startup execution receipt reaching `0x418a44`; its 56 ready and five auxiliary list initializers and published anchors match the full native pseudocode. These two source groups require no selected source change.

The two power guard bodies `0x41bd92`/`0x41bde4` also have current selected source hashes equal to the prior 14-case stock/source receipt, with all 164 bytes across both bodies visited. Their ordered power-control calls, request-bit changes and bounded status polling match under synthetic MMIO. Physical clock/power sequencing remains unqualified.

The selected named-ISA delay body `0x41d1c0` hash matches the prior 780-case stock/source receipt covering all 80 native bytes, including FPU rounding modes and a genuine external ROM cycle-call boundary. The selected MSPI interrupt-status getter `0x4264ba` is bound structurally against the full native pseudocode and pinned Ambiq HAL 5.1.0 body: handle check, module register offsets, status/enable read order and return values match. This MSPI binding has no fresh current-source native execution receipt; physical interrupt timing remains unqualified.
