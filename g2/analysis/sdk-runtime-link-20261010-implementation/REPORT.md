# Official SDK runtime/placement compatibility experiment

## Finite result

Two compile/link-only experiments successfully combine the **unchanged official AmbiqSuite5.2.0 am_util_stdio.c** with its unchanged Apollo510B hello-world GNU linker script. Complete linked ELF files have zero undefined symbols without runtime mocks, syscall stubs, source aliases or vendor archives. A deliberately mixed hard/soft float call ABI fails as expected. The unchanged retained TLSF comparator still fails with undefined **printf, memcpy and __assert_func** when supplied this SDK formatter under compatible softfp call conventions. Therefore the SDK formatter is a genuine available logging implementation with its own public names, not a drop-in closure of TLSF's C-runtime/assert contract.

## Authentic inputs and recipes

sdk-receipts.json binds eleven exact source/build members to the user-downloaded official package SHA-256 `d9751350ef593b306838792a64a5620e4912c84ddf32dc9ff6aacd5cca049cad`. Every source retains its copyright/license notices. Extracted materials include gcc/iar startup, linker scripts, Makefiles, IAR project options and stdio/debug files. Original input files were not edited. Repository instructions, current P2 workflow, TLSF runtime-boundary report, consolidated tooling/runtime/memory references and supporting emulator instructions were read first. No production implementation/admission occurs here; all output is analysis-owned.

The SDK GNU recipe explicitly selects Cortex-M55, FABI=hard, FPU=auto; it normally groups libm/libc/libgcc/libstdc++ and HAL/BSP archives. The IAR project describes normal C/C++ runtime configuration, names __iar_program_start, and records numeric compiler options in iar-option-receipt.json. Numeric SDK project settings are not inferred application-producing flags or an identified IAR release. startup_iar.c declares __iar_program_start and IAR-specific stack/vector syntax. startup_gcc.c has data/ITCM copy and BSS zero loops followed by SystemInit/main. These authentic recipes reduce interface uncertainty but do not identify the stock producing configuration.

build.py reproduces two positive and two negative links. Exact commands/results are in recipes.json and named compile/link receipts. Compiler is installed Apple clang targeting ARM32 Cortex-M55, Thumb, O1, freestanding, no builtin library substitution, function/data sections. This is a compatibility substitute for the SDK recipe's arm-none-eabi-gcc, not a byte-producing IAR claim. GNU ARM ld uses the SDK script unchanged; **-e placement_probe** intentionally overrides its Reset_Handler entry. Neither original startup file is compiled or executed. placement-probe.c supplies only section markers and a function referencing authentic formatter/ITCM code; it is not a reset handler, vector table, HAL mock or hardware-ready firmware. No garbage collection is used, so the complete compiled formatter's linkage is represented, not merely its retained integer subset.

## Placement and ABI findings

Both maps/ELFs establish:

* Executable MRAM begins at0x00410000 under the SDK script. probe_itcm VMA0 and MRAM LMA0x0041102C demonstrate the explicit copy contract. Initialized probe_data is at0x20000000 with load address0x00411038.
* Stack/heap markers lie at0x2007D000/0x2007C000; shared NOLOAD marker lies at0x20080000. Plain BSS begins0x20000004.
* Defining **AM_PART_APOLLO5_API** activates the unchanged formatter's doubled buffer and 4096-byte alignment: g_prfbuf moves from0x20000011 to0x20002000; aligned variant BSS begins0x20001000 and ends0x20002800. This macro is explicitly varied, not claimed recovered from stock. High-alignment input sections can therefore materially change region consumption even with identical linker script and entry.
* Both linked images record VFP-register argument ABI. Linking a soft-call-ABI probe against the hard-call-ABI formatter rejects with “uses VFP register arguments”. No --no-warn-mismatch, attribute editing or permissive ABI override is used.

verification.json and verify.py assert exact sampled placement, zero undefined symbols, hard-float attributes, macro-controlled alignment and both negative boundaries. No binary was run on an emulator or device. Compile/link success cannot validate FPU initialization, startup copy behavior, console delivery, buffer safety, locking or physical memory access.

## Remaining TLSF/runtime boundary

The SDK debug header enables am_util_debug_printf as a macro forwarding to **am_util_stdio_printf** under AM_DEBUG_PRINTF, otherwise disabling it. It does not define plain printf or __assert_func. The retained TLSF comparator's exact three unresolved names were independently read with nm; tlsf-sdk-negative.txt/map record genuine unresolved linkage against softfp SDK stdio. No assertion was disabled, no alias inserted, and no diagnostic stop mock adopted. The compile/link experiment thus preserves the exact missing C-runtime/header/diagnostic boundary instead of disguising it.

This does not revisit closed allocator operations or the earlier IAR memcpy relocation attempt. The prior missing producing ICCARM/ILINK release/options, DLIB composition, application assert override and IAR fragment/link handling remain required for exact reconstruction. The public GCC linker layout is different from the recorded stock IAR scatter loader at0x005E42B4/table0x0075D3C8, including stock ITCM destination0x40; it is an available recipe, not the G2 linker map. IAR uses .intvec/.textrw/SHARED_RW/RESOURCE_TABLE, while the tested GNU script uses .isr_vector/.itcm_text/.shared/.resource_table. Those names and initialization semantics must be reconciled from producing evidence before mixing toolchain-generated objects or applying a linker script to stock.

Next finite goal: locate the authentic application's assert-header override and precise logger-to-runtime binding, or obtain its producing IAR project/link configuration. Existing SDK example files alone do not supply those. A licensed compatible IAR toolchain/project would be needed for the previously blocked exact runtime-object link, which was not retried. General source completeness, byte equality and physical behavior are not established. Independent review is pending.

## Preservation and tools

Preservation receipt verifies3,799 prior sealed entries,110 audit inputs and four checkpoints, with no seal/input mismatches and index stable during this verification interval. The index differs from an older track sample because of concurrent workspace state; no index command was used here. No existing seals, sources, payloads, submodule pins or device were changed. No commit, push, publication or permission change occurred. The paused actual FlashDB provider extension was untouched.

Installed Ghidra/REA/Ablation were not needed: this finite goal concerns exact available build source, compiler attributes and linker diagnostics, fully inspected through archive hashes, unchanged C compilation and ELF/map tools. No shared Ghidra operation or ownership conflict was introduced.
