# Application state3 LP phase: launch result, busy wait and next state

**120 comparisons pass**:16 full all-LP wrapper/launch cases,96 application LP-phase compositions and8 original/public no-callback sleep preparation cases ending at WFI. Application outcomes:44 completed phase observations,52 bounded busy waits;20 cases inject an ISR. Source ../../components/touch/lp_application_offline/application.c,h composes the validated independent LP launch with compiled pinned public PDL sleep bodies. No function-entry stubs.

## Concrete application chain

State dispatch0x3d5e reads byte0x200009cc. State3 branches at0x3d68 to0x3e28, loading fixed context0x200004ec and calling0x7050 at0x3e2a. Wrapper7050 checks null, then passes first0/count4 to full launch6d74; null returns1. This confirms the directly observed application path uses all four LP slots.

The **launch return is discarded**. Instruction0x3e2e immediately calls critical-enter4492, replacing R0. There is no error comparison, retry of launch, counter check or explicit timeout in the selected wait loop:

```c
(void)start_all_lp(context);
saved = enter_critical();
while (common->status & 0x80) {
    (void)enter_deep_sleep();
    restore_critical(saved);
    saved = enter_critical();
}
restore_critical(saved);
if (common->status & 0x400) { state = 1; budget = 640; }
else                      { state = 2; budget = 160; }
```

State is byte0x200009cc; budget is u32 at0x200009c8. These are numeric application state/budget fields, **not established milliseconds**. State1/2 subsequently reach other active-scan/report paths at0x3d70/0x3da8. This batch stops before logs, timer configuration5d90 and the common deferred/report loop; it does not reconstruct the entire nonreturning application function3cb4.

## Failure and retention behavior

The prior LP batch established that new-range bridge/MRSS failure can return4 after setting busy/status0xa1. Here the application enters repeated sleep/busy checks without inspecting that error. A failed bridge case with no completion event remains state3/budget999 after the explicitly bounded three app-level restorations; no phase transition occurs. This is an offline software observation, **not evidence of hardware deadlock or missing real interrupts**.

Invalid prior mode3 can return1 before setting busy. In the tested initially-not-busy case, the app skips sleep and selects state2/budget160 anyway. Initial busy rejection0x40 waits for busy to clear rather than retrying the LP launch. A synthetic signal-detection ISR sets0x400, clears busy through the actual original/native ISR, and leads to state1/budget640; an injected completion with no signal leads to state2/budget160. No particular callback/IRQ timing is claimed reachable on hardware.

This means a future design must distinguish launch admission/error handling from eventual ISR completion; the existing app phase does not do so explicitly. No retry, watchdog, filter reinitialization or production patch is added here. Same-range frame-reload limits remain those in ../touch-lp-filter-closure-2026-10-08/REPORT.md.

## Critical and sleep boundaries

Original4492 reads PRIMASK then masks interrupts;449a restores the saved token. Sleep coordinatora58c separately enters/restores a nested critical section. Tests count **application** restoration boundaries, excluding the nested PM restoration. IRQ injection occurs only after app restoration when PRIMASK==0, using CPU-context save/restore around direct original/native ISR execution. Initial PRIMASK1 cases do not receive that synthetic delivery. Thus the test does not deliver an ordinary IRQ through a masked section or infer NVIC wake behavior.

Native-side sleep uses verbatim pinned PDL `Cy_SysPm_CpuEnterDeepSleep` and `Cy_SysPm_CpuEnterDeepSleepNoCallbacks`. Callback-root table is supplied zero. Critical providers remain original4492/449a. The PM callback executor addressa444 is bound but **not exercised**; real registered callback implementations/lifecycle remain outside this composition.

The coordinator conditionally executes callbacks for CHECK_READY, BEFORE_TRANSITION, AFTER_TRANSITION or CHECK_FAIL. Its return is ignored by the app; no nonzero-callback test or physical rejection scenario is claimed. The no-callback helper copies a u16 synthetic SFLASH key delay at0x0ffff152 to0x40030004, sets SCB SCR SLEEPDEEP mask4, then reaches WFI. Eight preparation cases vary delay0/1/0x8000/0xffff and SCR0/0xffffffff and compare side effects **before WFI**. They do not test physical sleep, wake timing or arbitrary SCR-mode execution; the application cases use the bounded emulator/synthetic event model.

## Selected public-source attribution

Pinned CapSense247a... `Cy_CapSense_ScanAllLpSlots` reproduces all20 bytes at7050..7064 with GNU13.3-Og and fixed peer binding6d75. Pinned PDL35f171... `Cy_SysPm_CpuEnterDeepSleep` reproduces104 bytes at a58c..a5f4 with explicit callback-root/peer addresses. Both have one complete-byte match. Macros/opaque types/address bindings are recorded; neither proves a complete SDK build or unique producer/compiler.

Public NoCallbacks compiles to36 bytes versus40 stock bytes including literal pools and is **not byte-exact attributed**. Its selected preparation behavior and its use in app composition pass; no40-byte equality claim follows. Distinct selected exact attribution is now438 bytes (prior314 + wrapper20 + coordinator104), separate from independent behavioral source closure and full firmware equality.

## Reproduce, preserve and continue

screen_public_sleep.py extracts/builds pinned PM bodies and emits the combined public-sleep.c into scratch. build_offline.py requires that path via --public-sleep-source, the existing pinned PDL object, GCC and scratch output. verify.py ELF runs120 cases. screen_public_wrapper.py records wrapper attribution. Input/source/compiler/ELF hashes, original disassembly and environment/bindings accompany this report.

Persistent actual RAM and MMIO are compared; compiler stack frames and register allocation are not asserted equal. Setup uses validated initialization/preparation source and actual reset-copied pointers, not full application startup. No commits, Git index, production firmware or device writes; prior sealed deliverables/110 inputs/4 checkpoints remain unchanged.

The nominal212-result/424-byte full-range window is unchanged and **not a declared history allocation**. Missing generated cycfg/link-map evidence and physical IRQ/sleep traces remain exact external-input boundaries. Independent next leads are timer/configuration5d90 following the state transitions, and pinned PDL callback executora444 if actual registered-PM lifecycle evidence is recovered. No whole-system exhaustion or hardware-safety conclusion is claimed.
