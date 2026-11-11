# C IQS recovery and reset policy

`r1/src/application/runtime/native_iqs_recovery.c` implements the ATI recovery
policy at `0x6f9e4` and reset/reconfigure wrapper at `0x6fce8` in ordinary C.
The existing IRQ worker now reaches these implementations. The lower error
audit (`0x41a40`) and controller configuration (`0x2f880`) remain explicit
unresolved dependencies; neither is replaced by a success stub.

Recovery logs the ATI error, invokes the audit, then posts touch event `0x20`.
It reads and increments the live consecutive-error byte, saturating at 255.
At five or more consecutive errors, if used retries are below three, it
increments used, clears consecutive, sets the existing slider flag, logs the
live retry value and posts close/reinitialization event `4`. Otherwise, used
retries at or above three log exhaustion and retain the state without a port
write. Below both limits it writes bytes `20 00` to register `0x33` and logs
re-ATI. No new state owners are introduced.

The reset wrapper logs reset, calls the lower configuration routine once and
logs completion. Provider status does not suppress continuation. Both policies
re-read logging modes at native decision boundaries; logged retry values are
loaded after those calls and separately for each sink.

The [machine-readable receipt](iqs-recovery-c-review.json) records 5,848 direct
stock/C comparisons across all consecutive and retry byte values with threshold
cross-products, changing logging modes, live provider mutations, and reset
status cases. Another 1,348 comparisons execute actual C event posting, IQS
ports, transport and registry against prepared kernel/device callbacks.
Both passes also check 30 independent side-effect oracle cases. Integer callee
saves, stack guards, PRIMASK and BASEPRI are checked.

A further 612 comparisons and 12 defined private-buffer fallback checks enter
through the actual C IRQ worker, detector, channel averaging and event path,
recovery policies, ports, transport and registry. All twelve compiled defects
are rejected, then unmodified production objects are rechecked. The
[REA receipts](iqs-recovery-rea-bytes.json) match both complete entry byte ranges
to the pinned raw firmware; they do not claim decompiler or instruction identity.

The normal R1 build compiles 836 units (754 application, 82 bootloader) and
composes relocatable objects with 77 application imports and 22 bootloader
linker imports. All 833 prior nongenerated objects are unchanged. The two
recovery imports are replaced by the real audit/configuration dependencies.
The R1 manifest check passes. Global `make sources-check` still reports the
pre-existing unlisted G2 `resident_rom_thumb_set.S`.

The probes model lower audit/configuration, logging, and storage providers;
prepared kernel/device callbacks do not establish physical transfers or timing.
Final application linking, runtime placement and device boot remain unverified.
Byte identity is not required by the current user instruction.
