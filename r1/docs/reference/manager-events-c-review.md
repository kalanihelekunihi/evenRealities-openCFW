# C manager hardware-event dispatch and reset request

`r1_manager_event_dispatch_46004` supplies the manager's reset/worker-exit policy in ordinary C. A second participating C unit wraps the pinned CMSIS architectural reset at stock `0x381a4`, without adding another reset-site capture. The existing checked peer-delete entry `0x4e9bc` now calls the source-owned `pm_peers_delete` and reports a nonzero result through the existing error logger. REA bytes authenticate all three entries and their referenced dispatcher literals.

The dispatcher preserves stock priority and ordering:

| Flag, in priority order | Sequence |
| --- | --- |
| `0x1` | Status 1, worker exit, sysctl sequence, 5,000-ms busy delay, reset |
| `0x2` | Status 2, worker exit, tag 2/site capture, reset |
| `0x100` | Checked peer deletion, health-cache clear, NV flag clear and aliased erased-address writes; 200-tick RTOS delay; status 2, worker exit, tag 8/site capture, 2,000-ms busy delay, reset |
| `0x200` | Typed memory-error message, worker exit, tag 9/site capture, 200-ms busy delay, retained assertion diagnostics and explicit architecture-transfer gate |
| `0x4` | Status 3, worker exit, sysctl sequence, 5,000-ms busy delay, reset |
| `0x8` | Status 4 and worker exit |
| `0x10` | Worker exit, including a second call when combined with `0x8` |

Each status uses the existing publisher `(kind=2, event=status, value=0, detail=0)`. Existing NV helpers consume the same six erased bytes through identical address pointers; the local words' unused trailing bytes are outside the comparison. The lower worker routine's native diagnostic says `thread exit start`; its implementation remains an explicit dependency.

**10,530 stock/C dispatch comparisons** cover all 128 relevant flag combinations, unknown/random bits, helper results, peer deletion failures, AIRCR values and both interrupt-mask states. Three additional standalone peer-wrapper comparisons pass. They verify call order, explicit arguments, all assertion strings and the terminal reset/assertion boundary. Helpers and delays are modeled using real Thumb return stubs; normal returns restore SP and saved registers, while all cases check stack guards, saved FP registers and masks.

The reset path executes the actual compiled CMSIS implementation. Both stock and C issue the exact virtual AIRCR value `(old & 0x700) | 0x05fa0004`, execute two DSB barriers around the write and reach the nonreturning NOP loop. BASEPRI and PRIMASK remain unchanged. The register is emulated memory: this proves the reset request, not a physical chip reset.

**1,404 additional comparisons** execute the actual status publisher, device/peer/charge helpers and source-owned ring storage. Ring full/wrap cases, charge values, advertising configurations and emitted event arguments agree with stock. External timestamp, critical-section, event and hardware-update services remain modeled.

All **256 dispatcher instruction bytes before the assertion transfer** execute. The final two-byte BLX into an even stack address containing `0xe7f00000` is observed before execution. Its source gate remains unresolved; the fixture does not replace or claim to validate that physical exception transition. Retained PC/LR capture is modeled here and private frame/register residue, APSR and concurrency are excluded.

Nine compiled defects are rejected: wrong event admission, reset tag/delay, erased address, peer-error admission, omitted sysctl action, wrong status, cleared BASEPRI and lost priority-group preservation. The normal build compiles **860 units**, completes both relocatable compositions and has no duplicate strong symbols. All **848 prior nongenerated objects** remain identical. Direct/integrated dispatcher and reset objects match the normal build. The manifest adds two participating units using existing profiles; previous exclusions and source-plan selections are unchanged. No mutable persistent state is added and R1 source validation passes.

The broad manager-dispatch import closes. `r1_manager_workers_exit_46bac`, `r1_health_clear_all_caches` and `r1_manager_assertion_stack_transfer` become explicit lower imports, changing application imports from 64 to **66**; bootloader linker imports remain **22**. These implementations, physical reset/peripheral behavior, full application linking and boot remain unfinished.

[Machine receipt](manager-events-c-review.json) binds sources, CMSIS header, REA evidence, normal reports and ignored fixtures under `build/goal-r1-manager-events-c/`.
