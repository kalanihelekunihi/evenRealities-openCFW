# Independent SDK formatter/link review

PASS: two unchanged SDK formatter/linker compatibility builds independently replayed, and both intended negative links failed. Twenty checks pass: downloaded SDK archive identity, eleven byte-exact archive members, exact positive ELF/placement/attribute verification receipts, six byte-identical rebuilt objects and negative return statuses. Compiler/source inputs copied to audit-owned output; existing inputs and seals read only. No device/canonical/Git/shared GUI changes or blocked FlashDB provider work.

## Authentic scope

Downloaded AmbiqSuite5.2.0 archive SHA d9751350ef593b306838792a64a5620e4912c84ddf32dc9ff6aacd5cca049cad authenticated. Exact stdio/debug, GNU/IAR startup/project/link files match named ZIP members, retaining notices. Neither original startup is compiled/executed. Actual compiled units are unchanged am_util_stdio.c plus explicit placement-probe.c markers. Probe defines no reset/vector/HAL/system runtime implementation. GNU script is unchanged, entry intentionally overridden to placement_probe. No GC hides formatter references; no archive/syscall/runtime mock is supplied. plain-stdio.o independently has no undefined symbols. Positive maps contain the two intended objects; zero undefined symbols is genuine link closure of this small compatibility specimen.

Apple clang21 Cortex-M55 hard-float is a substitute compiler, not the SDK GNU producer and not original IAR. GNU ld2.47 script compatibility does not authenticate original main ICF. Full ELF hashes and emitted object bytes reproduce; no original firmware compiled-byte comparison is involved. SDK project numeric IAR settings do not uniquely identify stock flags/release.

## Placement and negative controls

Both copies reproduce ITCM VMA0 with MRAM LMA41102C, probe_data20000000/LMA411038, shared NOLOAD20080000, heap2007C000 and stack2007D000. AM_PART_APOLLO5_API macro variant moves g_prfbuf from20000011 to4096-aligned20002000 and BSS boundaries from20000004 to20001000..20002800. This is an explicitly varied candidate macro, not recovered stock configuration. Final linked placement is proven; startup copy, BSS clearing, initial SP/FPU/cache/MPU behavior is not.

Compatible hard-float objects link. Soft-call probe plus hard-call formatter fails with VFP register argument diagnostic, without mismatch suppression or attribute changes. VFP argument attributes establish the recorded object interface, not all runtime floating-point safety. No emulator/device instruction execution occurred.

Retained TLSF comparator plus genuine softfp formatter fails with exact unresolved printf,memcpy,__assert_func. Thus the second negative control is compatible call-ABI linkage failure from missing symbol contracts, not disguised mixed-FABI rejection. No alias, assert disabling, trap or stub closes those names. SDK am_util_debug_printf macro forwarding is not a plain printf definition.

## What zero undefined does not close

Formatter owns g_pfnCharPrint/g_pfnCharGet BSS callback slots. am_util_stdio_printf returns0 immediately when g_pfnCharPrint is null; otherwise it formats and calls configured callback. Probe never calls am_util_stdio_printf_init. Consequently a hypothetical correctly initialized execution would have no output until callback setup; compile/link success says nothing about output delivery. This is an authentic configurable dependency, not a placeholder provider, but remains a runtime binding obligation. Float text correctness, buffer limits/reentrancy/locking and formatter execution remain untested.

TLSF remaining gaps: stock printf/logging variadic front end4733EE, formatter473036, buffer2006B930/callback200742F0 must be bound to source and original ABI rather than replacing them with SDK's public namespace; original memcpy439BE4 entry/interior ranges and IAR fragment relocation/link constraints remain; stock assert4D09B4 expression/file/line ABI and BKPTAB/conditional continuation differ from GNU-header __assert_func. Authentic override/header and original producing runtime/link configuration are needed. Neither SDK example ICF nor GCC startup sections establish original main scatterloader5E42B4/table75D3C8/ITCM40 placement.

## Actionable next finite test

For executable progress within available public source, test the unchanged formatter's bounded buffer API (am_util_stdio_sprintf or equivalent exported function) with small integer/float/format cases using the same exact object, explicit initialized RAM and return checks. Keep this separate from callback/hardware delivery; do not introduce printf aliases or assert/memcpy placeholders. Because valid-memory-write hooks have caused Unicorn IT-state corruption, retain instrument-free control and final RAM/code guards and report per-store limitations. This tests an unexecuted aspect of the linked specimen without touching paused actual FlashDB providers.

For authentic TLSF integration, the next input is actual application's assert-header/logger-runtime binding or producing IAR project/DLIB/ICF, not another SDK marker link. Obtaining/reviewing that input must respect existing access boundaries; the previously blocked exact runtime-object link is not retried here. No full-source, all-input, startup/hardware or byte-identical stock claim is supported.

Artifacts: build.py and verify.py replay recipes, checks.json, verification.json, recipes.json, positive ELFs/maps, ABI-rejection and TLSF unresolved diagnostics. Owner: g2/analysis/sdk-runtime-link-20261010-implementation/REPORT.md.
