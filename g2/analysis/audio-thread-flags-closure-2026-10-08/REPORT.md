# Apollo audio thread-flags provider: actual nonwaiting notification paths

**1,440 fresh three-way PASS cases**: original449238, independent [flags.c](../../components/audio/thread_flags_offline/flags.c), and selected official CMSIS-FreeRTOSv10.5.1 osThreadFlagsSet body. Actual original IRQ-context44900e and generic notify task455c48/ISR455dc0 providers execute on all sides, including critical providers4420d0/4420e8 and5fa0a4/5fa0ba. **No child entry stubs or result models.** This closes a selected provider boundary left by [notification-to-PCM foundation](../audio-notification-pcm-2026-10-06/REPORT.md); earlier328 calls/inventory counts were not rerun here.

## Interface and behavior

NULL thread or flags with bit31 set returnsFFFFFFFC(-4) without notify calls. Valid user flags are low31 bits, unlike case event-group low24 bits. Wrapper calls generic notify index0 twice: action1 ORs requested bits, then action0 queries current value into return slot. Notify value is TCB+68, state byte+6C. Tested previous states0(not waiting)/2(received) become2 even when flags0. Thus osThreadFlagsSet(thread,0) is not a pure state-neutral query.

Returned flags include existing notification bits, not just requested flags. Existing high-bit values are included as explicitly synthetic kernel-level contamination fixtures, not valid prior CMSIS user flags; a returned high bit cannot automatically be interpreted as a successful user mask. Provider return statuses are ignored by wrapper; these tested actions/states succeed. State1(waiting), task unblock/ready-list manipulation and wake failure remain excluded.

Audio enqueue foundation uses400000(bit22), and actual static flag dispatcher53cdac routes bit22 to message loop53cd62 and bit23(800000) to AUD_ThreadExit53cdc2, in that order if both set. Dispatcher/task-exit is static disassembly here, **not executed by these tests**. Flags carry no PCM pointer, period identity, ownership or completion token. A successful provider update does not prove task selection or immutable PCM lifetime.

## Context and masking evidence

IPSR0/15, PRIMASK0/1, BASEPRI0/10/30, scheduler-running0/1, old values0/100/80000000, nonwaiting states0/2 and flags0/400000/800000/7FFFFFFF/80000000 across NULL/allocated prefix inputs. Original context checks actual scheduler globals20074a3c/20074a58; no synthetic context function replaces it. Valid calls choose task/ISR provider accordingly, with exactly two verified calls/action arguments.

Every notification-field write asserts BASEPRI30. ISR providers restore input BASEPRI; task critical depth0 exits by clearing BASEPRI0, including selected synthetic startup inputs that entered with nonzero BASEPRI. PRIMASK is preserved. Scheduler-not-started context can choose task path despite masked inputs; this is executed context behavior, **not a claim those combinations occur in hardware or that task critical sections generally preserve arbitrary initial masks**. Waiting/yield paths fail if entered; no PendSV write expected for tested nonwaiting tasks.

The TCB notification prefix is synthetic, other bytes guarded, no fully initialized/live TCB claimed. Cortex-M4-compatible instruction profile emulates selected code from authenticated Apollo510 Cortex-M55 image (load438000, header32, SHA36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863). No M55/vector/exception delivery or actual scheduler trace. Scoped write hooks and explicit semantic postconditions check value/state/mask/provider calls; no inherited broad-hook diagnostic trace receives coverage credit.

## Public source and next actionable lead

Official CMSIS-FreeRTOS pin d213f261b5be6bb29a7cce8b84071706b72f4d53 body compiled with explicit type/action/macro mappings to actual generic providers; full source/license already retained in preceding case-event-flags batch. Original context is a common peer, not independent proof of complete public IRQ-context configuration or whole-kernel release. Receipt records body/source/scaffold/tool/ELF hashes.

Next bounded source targets are actual state1 notification wake/wait or initialized audio dispatcher table20073fbc, and AUD_ThreadExit53cdc2 queue/thread deletion calls. Those remain available in the locked image; missing runtime traces limit ownership/scheduling conclusions, not source analysis. Case event close/delete/quiesce/drain is still unbound. Global dependency/source exhaustion is **not** reached.

Build with build_offline.py, run opencfw venv verify.py. All851 prior sealed entries,110 audit inputs and4 checkpoints verified unchanged; no commits,index,production firmware/device writes. New tests are separate from foundation inventory and prior bounded equivalence counts.
