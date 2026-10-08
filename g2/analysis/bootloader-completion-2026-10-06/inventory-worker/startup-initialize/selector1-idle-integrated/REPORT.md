# Integrated selector1 and idle-helper successor

`8e255c6effef3c7d685f5d0aa98a163ebf163314be8c96dec958d806a9114d0c` is a separately frozen, validated successor to preservedc711fbf4. **209objects, seven exact-image integration cases and59 additional receipt files PASS**, zero frozen-input mismatches and exact ELF reproduction from frozen objects. See candidate-validation.json; immutable ELF/inputs/receipts are under `g2/build/bootloader-completion/selector1-idle-integrated/<hash>/`. c711, earlier checkpoints and shared129a remain unchanged. No commits/index/hardware changes.

## What is integrated

The initialized DATA installs selector1 using its compiler-owned pointer and native source mask707c10f.1371bytes match the locked initializer after declared native selector and two teardown-pointer normalization, including pad/record return.18selector1 cases cover all472original instruction bytes on thisexactELF. Selectors3/17 still pass installed direct/natural proofs;1400root fixtures run actual scatter-installed DATA. The native deferred-idle cleanup helper is linked, with24empty/one/two-entry/ownership comparisons and three actual-heap drain cases. Its callable alias418a98 is defined; **idle task entry4189ac remains an unimplemented original-address contract**, so linked cleanup alone does not establish live idle scheduling. Existing source components contain these bodies.

Both source segments stay within their original64KiB bounds: text65408bytes and source_cache65532bytes. A previously linked46-byte TON gate moved into the first segment to make room. The new selector1 object uses softfp compilation to match thiscandidate's link attributes; its integer-only interface is separately instruction tested. The prior standalone hard-ABI addon is preserved. No linker ABI mismatch was suppressed.

All47affected regressions PASS, including timer/helpers, PCM2.2 branches, clock/cache/UART/ADC/IOM/queue/kernel families and585alignment mappings. Runtime260, native teardown512 and actual allocator3 remain passing. Integration keeps startup/logger/peripheral models; separately native root/selector/ownership proofs do not remove these models or imply whole-firmware source completeness.

## New scheduler evidence and its precise limit

Four actual-instruction PendSV comparisons cover basic and FP-high-register save/select/restore, with history wrap0/63. Locked and compiled source agree on outgoing frame/TCB stack pointer, selected task, R4-R11,S16-S31, PSP, BASEPRI and EXC_RETURN. Execution stops beforeBX EXC_RETURN. S0-S15/FPSCR hardware/lazy stacking, automatic exception unstacking/task entry and MVE/VPR state are unverified.

The backend capability probe executes the actual locked BXr3 at41b372 with a basic synthetic frame and IPSR0/14. Both yield Unicorn interrupt8, PCfffffffc, unchangedPSP and no unstackedR0. Since NVIC active-exception state is not established, this is a limitation of the current test setup, not a proof of firmware fault or complete emulator incapability. Closing it requires an emulator profile that establishes real exception entry/active state and Cortex-M55 FP/security configuration, or an architectural trace. A custom Python pop must not be called architectural exception-return validation.

Official [CMSIS Cortex-M55 header](https://raw.githubusercontent.com/ARM-software/CMSIS_5/d23a6949a0331ca96853bcd98b0fdcc4db47184c/CMSIS/Core/Include/core_cm55.h) and [FreeRTOS M55 port assembly](https://raw.githubusercontent.com/FreeRTOS/FreeRTOS-Kernel/def7d2df2b0506d3d249334974f51e427c17a41c/portable/IAR/ARM_CM55_NTZ/non_secure/portasm.s) corroborate EXC_RETURNFType and conditional S16-S31 handling. Downloaded at existing gitlink/pinned upstream commits, hashes in upstream/provenance.json. Port.c documents tick suppression; this does not establish an exact producing SDK/port version for stock firmware. Arm manual web endpoints redirected to inaccessible support pages; no undocumented architecture assumption is promoted to proof.

## Tick-suppression body

Separately compiled `tickless/tickless.c` reconstructs locked41b754..41b818.192instruction comparisons PASS and cover all196bytes, including reject/cap/sleep-hook decisions, counter wrap, timer alignment and tick-step saturation. Timer read/program/enable/clear, sleep-confirm, pre/post hooks and tick-step are recorded controlled boundaries; WFI is modeled as immediate wake. Thisaddon is **not linked into the209object candidate**. Its immutable evidence is underg2/build/bootloader-completion/tickless-body/<addonhash>/.

The body caps expected scheduler ticks to20027128, masksIRQ, confirms sleep, subtracts elapsed timer counts from expected*counts_per_tick20027124, invokes pre-sleep and optionallyWFI, invokes post-sleep, aligns20027120 to the elapsed whole-tick boundary, enables/clears/re-arms the timer, advances min(elapsed_ticks,expected), then enablesIRQ. The locked wrap usesUINT32_MAX-before rather than an invented2^32 correction. Finite nonzero period and controlled callbacks only: this does not prove physical elapsed time, interrupt latency or safe concurrent scheduler mutation.

## Remaining promotion boundary

This is a validated unpromoted offline source candidate, not an official byte-identical bundle or hardware-ready image. Shared startup41c4b4 alias, remaining selectors, idle entry4189ac, actual exception-return/FP-low/lazy state, asynchronous IRQ/timer/WFI behavior and resident ROM remain separate frontiers. Historical selector17 verifierabb854 copy is still unavailable; its original manifest remains unchanged. New source-boundary evidence is independently reconciled. Next useful code work is the idle-entry/tickless dependency chain4181e4/418a00/41f424/41f440/41f4b6/41b630/418394, using existing source where present, with genuine architectural exception-return testing treated as its own tooling boundary.

QEMU11.1.2 is installed and advertisesmps3-an547(Cortex-M55). This offers an actionable next offline architecture harness for real NVIC exception entry/return; it is not an Apollo510 board model and must not be presented as firmware/hardware validation. No new hardware input is required to begin that bounded core test.
