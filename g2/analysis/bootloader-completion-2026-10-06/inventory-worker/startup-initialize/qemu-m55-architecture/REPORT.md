# Cortex-M55 architectural exception and ownership tests

Nine corrected scenarios PASS: basic and FP task contexts, each with ownership 0 (stack+TCB), 1 (TCB only), and 2 (neither). Test-only vector/task setup runs reconstructed SVC, IRQ/PendSV, ready selection, task deletion, allocator and idle-cleanup source on QEMU 11.1.2 `mps3-an547`. No firmware component code changed for this correction; 209-object candidate remains separate.

## Original fault diagnosis

The original failure ELF, trace, harness and partial three-basic-PASS receipt are preserved in `fp-failure-preserved/`. Original IRQ return already completed successfully in QEMU's exception log. The harness incorrectly interpreted an extended frame as FP words followed by core words. QEMU release `m_helper.c` lines1264..1277 puts core R0..xPSR at offsets0..28; FP S0 begins +0x20 and FPSCR is +0x60 (lines1319..1337). The incorrect reader then tested an FP word as xPSR, triggering an assertion.

Assertion reporting itself faulted at `0x10aa`, compiler-generated `LE lr`. Harness `VMSR FPSCR` had set0x00400000, thereby clearing LTPSIZE. QEMU `translate.c` lines5648..5672 explicitly raises INVSTATE for non-tail-predicated LE with active FP and LTPSIZE !=4. CMSIS pinned Cortex-M55 header defines LTPSIZE at bits16..18. Correct fixture FPSCR0x00440000 preserves the intended rounding bits and sets LTPSIZE4. A targeted negative control deliberately uses LTPSIZE0 and invokes the reporting loop: it reproduces CFSR0x00020000/HFSR0x40000000/PC0x10aa. With LTPSIZE0 but without that loop, corrected frame checks also passed; thus LTPSIZE is a loop precondition, not an unconditional FP exception-return requirement.

Frame assertions now read S0 at hardware-frame word8, FPSCR at24. After software PSPLIM/EXC_RETURN/R4..R11 and S16..S31 save, corresponding outgoing-frame indices are34 and50. No FP path was skipped. Linker BSS address is now explicit20040000; the empty DATA section had previously left static stacks in ITCM. Basic scenarios rerun successfully with DTCM static stacks.

## What is established

Actual QEMU-modeled SVC first-task return, IRQ basic/extended stack/unstack, preserved S0/S16/S31/FPSCR sentinels, outgoing FP-high save, basic idle-task PendSV return, and deferred idle reclamation execute. Observed frees are2/1/0 and heap returns to81904-byte baseline in all three ownership cases. IRQ handler VMRS forces pending lazy low-FP save before inspecting the frame.

## Limits

Synthetic coherent tasks/ready lists and test-only idle entry. This does not run the locked official ELF, model Apollo510 peripherals, validate real IRQ latency, stress concurrent deletion, prove full VPR/MVE register preservation, or prove repeated preemption/resumption of a previously running FP task. FP IRQ return and incoming PendSV FP-task restoration are both tested. The incoming task has a synthetic coherent extended frame, not a task previously preempted and resumed. Full stock idle entry0x4189ac and tickless dependency chain remain source gaps. No hardware writes or commits occurred.

Official source evidence: [QEMU m_helper.c v11.1.2](https://raw.githubusercontent.com/qemu/qemu/v11.1.2/target/arm/tcg/m_helper.c), [QEMU translate.c v11.1.2](https://raw.githubusercontent.com/qemu/qemu/v11.1.2/target/arm/tcg/translate.c), and pinned [CMSIS Cortex-M55 header](https://raw.githubusercontent.com/ARM-software/CMSIS_5/d23a6949a0331ca96853bcd98b0fdcc4db47184c/CMSIS/Core/Include/core_cm55.h). Downloaded QEMU source hashes, tool identity, source copies, six ELFs/objects/logs and negative control are recorded in frozen-evidence.json.

## Incoming FP extension and preserved counterexample

Three additional cases restore an incoming synthetic extended FP task through real modeled PendSV exception return after ownership cleanup. R4-R11, R0/R12, S0/S16/S31, exact FPSCR0x00440000 and CONTROL are checked. All nine scenarios PASS. Initial synthetic incoming xPSR0x01000000 omitted secure FP active bit SFPA; the first FP access initialized FPSCR to0x00040000. QEMU m_helper.c restores CONTROL.SFPA from stacked xPSR (lines1879..1882), and the fixture now uses coherent xPSR0x01100000. The failed image/log/source are preserved in incoming-sfpa-counterexample/. No FPSCR assertion was relaxed. This is secure MPS3 context evidence, not a claim about the locked firmware's actual security configuration.

Reproduce from repo root: `python3 .../qemu-m55-architecture/build.py`, then `python3 .../qemu-m55-architecture/run_scenarios.py`. Paths use the full directory of this report. The former compiles only synthetic guests in /tmp; the latter runs QEMU. Six-scenario frozen evidence remains preserved; nine-scenario-evidence.json records the successor.
