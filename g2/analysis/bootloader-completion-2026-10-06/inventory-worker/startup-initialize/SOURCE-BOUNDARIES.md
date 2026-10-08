# Current bounded source frontiers

- Preserved c711fbf4:7integration cases+54additional receipts,207inputs and exact ELF reproduction. Shared129a unchanged.
- PCM2.2 selector1: new C/body proof18cases/all472bytes, native TON/timer/delay/cache dependencies. Component source added; not installed in c711. Next: compiler pointer/source-mask successor and exact-image tests.
- Idle drain418a98: new C,24cases/all60bytes; actual heap drain3ownership cases. Component source added; standalone addon, not integrated successor.
- Non-FP PendSV save/select/restore:2actual-instruction tests up to BX EXC_RETURN, native ready selection; hardware exception return/task entry and FP extended frames unverified.
- Idle caller4189ac: newly identified missing corpus function; direct bytes and pseudocode recovered. Tick-suppression/WFI branch41b754 remains to bound.
- Selectors4..7,9..13,19..23 and other full-startup paths are not claimed closed. Timer/ROM/peripheral acknowledgement and broader boot models remain separate.
- Historical selector17 abb854 verifier snapshot unavailable. Later expanded evidence reconciles separately; historical receipts/manifests unchanged.

## Integrated8e255c6e continuation

- Selector1 now compiler-installed in new209object successor; seven integration cases+59additional receipts PASS, exact frozen-object ELF reproduction. c711/shared129a unchanged.
- Idle drain now linked and directly verified24cases+actualheap3; idle entry4189ac itself remains an original-address contract.
- PendSV extended to4basic/FP-high-register instruction cases. S16-S31 conditional state proven; exception unstacking, FP-low/lazy/MVE and actual task entry remain unverified.
- Bounded exception-return probe yieldsinterrupt8 with manually seededIPSR/basic frame; activeNVIC state not established. Need an architectural entry/return emulator profile or trace to close that boundary.
- Tickless body41b754 newly reconstructed;192cases/all196bytes with explicit timer/hook/WFI controls, separate addon not integrated. Resolve its real timer/scheduler callees and idle entry next.

- Next architectural test is feasible with installedQEMU11.1.2mps3-an547M55. Build a bounded core/NVIC entry-return harness; retain distinction from Apollo510 peripherals and working firmware.
