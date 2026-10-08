# Idle/tick-step/STIMER source chain

**205 original-instruction versus compiled-source comparisons PASS** on the exact ELF identified in evidence.json. Locked bootloader SHA f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5, load410000. New C bodies/interfaces are idle_chain.c/.h; tickless_native.c composes the previously tested tickless body with these native dependencies and the separately verified sleep_policy.c. No shared source or candidate is promoted.

## Recovered behavior

| Stock address | Native behavior / test limit |
|---|---|
|418394..418408| Tick-step asserts if unsigned tick+step passes next-unblock. Equality asserts suspended!=0 and step!=0, enters actual critical helper, increments pending ticks, decrements step, then advances current ticks. This preserves the last tick for scheduler resume.110/116 bytes visited; three terminal assertion self-branches stop after the faulting write. |
|41f424..41f440 and422aac..422ac8| Counter wrapper and three-read sampler execute natively. Mask PRIMASK during three volatile reads at40008804; restore it before copying results. Equal first pair -> second; otherwise third. All56bytes visited. |
|41f440..41f4ac| STIMER delta compare: channel>=8 returns5. Poll until counter differs from per-channel last-write snapshot and snapshot+1; mask interrupts, subtract elapsed counts+3 from requested delta. If too small write1 and return08000000; otherwise return0. Write compare at40008820+4*channel, record a fresh counter read, restore prior PRIMASK. All108bytes visited, including wrap fixture. A counter that fails to progress can keep polling: finite advancing-MMIO tests do not prove physical clock availability. |
|41f4b6..41f4c0| **STIMER interrupt clear**, not timer enable: write bits to40008908 then read status40008904. All10bytes. W1C silicon effects are not emulated. |
|41b630..41b64c| Clear NVIC pending bit for nonnegative signed16 IRQ number, ignored for negative. IRQ32 writes bit0 toE000E284. All28bytes. Pending interrupt delivery is not tested here. |
|41b5e8..41b5f4 /41b5f4..41b5f6| Pre-sleep calls41a71e(1), then returns0 regardless of its result; post-sleep returns immediately. All14bytes. Deeper sleep routine is an explicit controlled boundary. Therefore the stock tickless body's direct WFI branch is normally bypassed; actual sleep is inside the deeper routine. |
|4189ac..4189fa| Complete loop control reconstructed: cleanup, optional yield for >=2 idle-ready tasks, expected-idle threshold, suspend, next-unblock>=ticks assertion, recheck, optional tickless call, resume.76/78 bytes visited; terminal assertion self-loop is bounded after its faulting write. Cleanup/reschedule/suspend/resume remain modeled lifecycle calls. |

Eight additional IRQ-save bytes at41b8ec execute natively. Actual BASEPRI critical helpers from kernel_runtime.c, native expected-idle/confirm-sleep helpers, counter/sampler, compare/clear wrappers and tick-step execute together. Full-idle comparisons stop on its second cleanup call; they exercise eligible sleep, abort from pending work and post-suspend expected0/1/long cases. Combined stock tickless coverage is160/196bytes with actual pre-sleep return0; the earlier192-fixture oracle separately covered its entire196bytes with controlled hooks. Do not combine these into a claim that real WFI/wake was tested.

## Official references and corrections

Pinned [Ambiq STIMER source](https://raw.githubusercontent.com/AmbiqMicro/ambiqhal_ambiq/5efc0228528a8adce5eae0d226fac85d2551eb3b/mcu/apollo510/hal/am_hal_stimer.c), downloaded with hash in upstream/provenance.json, corroborates triple-read selection (line307), delta compensation and prior-write polling (line409), and STMINTCLR write/status read (line825). The SDK notes that compare writes accept deltas and delayed/stale interrupts can still occur. Numeric3 is **counter counts**, not milliseconds. This does not identify the exact SDK version that produced the locked binary.

Pinned FreeRTOS-Kernel tasks.c at def7d2df2b0506d3d249334974f51e427c17a41c, cached in ../runtime-action-416200/upstream/, contains vTaskStepTick at2581 with the same equality/pended-tick semantics. Original locked bytes remain the oracle.

Prior tickless-only artifacts use the label timer_enable for41f4b6. Preserve those immutable receipts; this successor corrects that interpretation to stimer_interrupt_clear. No new claim that the hardware timer is enabled follows from that write.

## Candidate and model boundaries

Nine frozen QEMU architectural scenarios and negative controls are preserved; all recorded nine-scenario evidence hashes still match. Exact209-object candidate8e255c6e remains unchanged. This new combined addon is not linked into that candidate and is not a byte-identical firmware bundle.

Lifecycle/deep-sleep dependencies are not closed yet: full idle still models cleanup/reschedule/suspend/resume, and41a71e owns the actual sleep transition. There is no Apollo510 timer, power state, wake latency or ISR concurrency proof. Consequently an exact candidate successor must not be marked full-idle/native-sleep complete from these tests. Existing two source slots also have only128/4bytes spare; this addon requires deliberate source layout rather than overflowing those limits.

Next source-driven batch: bind native cleanup/suspend/resume/reschedule with coherent lists in the full idle test, and recover/bind41a71e's official sysctrl-sleep dependencies. Then define a separately frozen candidate successor and run its own exact-image integration/affected regressions. A real Apollo trace is needed for peripheral timing, not for the remaining source recovery. No commit, device write or credential change.

Reproduce: run this directory's build.py with python3; run verify.py with ~/.local/share/opencfw/venv/bin/python. Builds only /tmp addon files. Frozen source/object/ELF/test hashes are in evidence.json.
