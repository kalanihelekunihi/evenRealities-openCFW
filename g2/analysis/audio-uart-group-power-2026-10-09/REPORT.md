# UART grouped power, callback boundaries and polling

**240 original-instruction/source comparisons PASS**, including ordered MMIO reads/writes and arguments/delays. Final source ELF and input hashes bind in [receipt](reproduction-receipt.json), [results](results.json). New reconstructed UART-only predicate0x47F6F2, optional pre/post callback dispatch0x48032C/0x480342; generic group control0x480312 and status check0x480826 are repeated already-known behavior, not newly discovered functions. Descriptor source is reused unchanged. [Readable C and interfaces](../../components/audio/uart_group_power_offline/providers.c), [pseudocode](pseudocode.md).

## Critical correction to prior interrupt-clear report

[Direct unchanged instruction traces](interrupt-clear-difference.json) show **stock and compiled source both write IEC0x40039044, then read MIS0x40039040**. Both also fault on the unmapped NULL handle fixture before validation. The prior sealed UART power/configuration report inferred stock lacked these operations from decompiler output; that inference was wrong. This additive correction supersedes that portion of the prior report. No sealed prior evidence is rewritten. These matching traces establish fixture access order, not physical register side effects or general NULL safety.

## Recovered contracts

UART domains11..14 use enable register40021004, individual masks200/400/800/1000, and status register40021008 with shared mask1E00. Predicate0x47F6F2 performs descriptor lookup after byte narrowing. For UART group it first reads enable register and tests1E00; only if nonzero does it reread and test the selected device mask. It returns0 when another group device remains enabled while selected device is disabled. In disable0x47F7AE, zero skips the group-completion poll and grouped callback. Group status must not be treated as per-UART acknowledgement. Fixtures compare both reads, including short-circuit one-read cases and wrapped267..270 inputs.

Pre/post callback pointers are RAM slots2007327C/20073280; NULL returns0. Group callback pointer20073274 receives action/enable narrowed to bytes and original metadata pointer. Non-NULL tests stop before external body; they do not synthesize successful callback effects or scheduler transitions. Callback registration, actual chosen board bodies and preemption remain open.

Status-check0x480826 reads before decrementing budget and invokes delay0x4807A0 with1 only after unsuccessful read with remaining budget. Thus budget5 permits6 reads and5 delay calls on a stalled fixture, returning4. Nonzero byte-narrowed fifth argument waits for equality, zero for inequality;256 becomes0,257 becomes1. Expected value is not masked; expected bits outside mask can prevent equality. Synthetic register changes after selected delays validate rereading and exit, not elapsed wall time or hardware readiness.

Source wait is reconstructed from the same already-sealed timing behavior; selected delay remains an explicit mocked boundary. IRQ/power enable-disable enclosing composition is not claimed complete by these helper tests. Native reached addresses are guarded; original instructions stepped unchanged. No device, DMA, delivered IRQ, concurrency or physical shutdown proof.

The completed RX pressure result remains scoped: copies accepted prefixes, ignores accepted count and resets staging; synthetic rejected suffix is lost on that path, not evidence of measured hardware loss.

## Remaining concrete source leads

Compose UART subset enable0x47F5B8/disable0x47F7AE with these helpers, existing descriptor and IRQ-mask source. Recover actual callback installation/targets and validate bodies before replacing callback cuts. Existing clock dispatch/ownership is already source-backed and need not be reimplemented. RX receiver0x57E136 and notifier0x455DC0, channel3 IRQ/drain routing, and formatter call/preemption evidence remain useful source leads. No global source-exhaustion or external-input blocker is asserted.

All prior seals,110inputs and fourcheckpoints verified unchanged. Git index differs from the original baseline due to concurrent staging observed during this batch; this worker issued no Git mutations and preserved the current index. No commits, production/device/shared-state edits. This is author offline validation, not independent whole-firmware completion or source byte equality.
