# Bootloader reset sequencing in C

`r1/src/bootloader/runtime/reset.c` now provides Reset_Handler. It copies aligned
initialized words in descending order from __etext to the RAM span
[__data_start__, __bss_start__), calls the existing SystemInit, then enters the
existing C CRT `_start`. The CRT clears BSS and calls main. Volatile word
accesses retain the copy operations without introducing a libc helper.

The sequence follows the pinned Nordic GCC startup source, including initialized
registration data inserted before BSS. The captured compilation does not enable
the SDK optional skip-copy or early-BSS-clear startup variants. Those variants
are not supported by this C entry. Aligned, ordered linker ranges and an initial
stack supplied by the vector table are prerequisites.

At this reset checkpoint, the manifest generated `r1_startup_vectors.S` from
the pinned SDK source with its reset body removed. The later
[bootloader vector review](bootloader-vector-c-review.md) records its C
replacement, including the stack/heap reservations and weak handlers.

## Executed validation

`build/goal-r1-boot-reset-c/verify.py` passes 960 reset/CRT handoff cases across
30 layouts: initialized data sizes 0,4,8,64,76,512 and BSS sizes 0,4,16,256,4096.
Tests vary entry at reset or CRT, interrupt masks and SystemInit effects on data,
BSS and PRIMASK. They check data-copy boundaries, BSS-clear boundaries, unmodified
FLASH, ordered SystemInit/main calls, call alignment, mask preservation and the
terminal CRT loop if main returns. SystemInit and main are modeled boundaries.
BSS remains poisoned until the CRT stage, including at the SystemInit boundary.

The same contract cases also pass with the original compiled Nordic assembly
reset substituted for the C reset. The baseline receipt identifies the actual
substituted object hash. Four compiled defects—omitted copying, skipped first
word, omitted SystemInit and premature BSS clearing—are detected; a final clean
C run passes afterward.

`production.py` loads the final ELF's FLASH load segments at their physical load
addresses and poisons RAM. It takes SP and reset PC from the actual vector at
0xF8000 and passes 16 handoffs with the real linker layout: 76 initialized bytes
and 9636 BSS bytes. The vector supplies SP=0x20040000 and the Thumb C reset entry.
These tests also model SystemInit and main; they do not execute hardware errata
setup or DFU startup. Emulated handoff is not physical reset validation.

## Build audit and limits

`build/sources-goal-r1-boot-reset-c/report.json`: 778/778 units compile, comprising
696 application and 82 bootloader units, without failures or duplicate strong
symbols. Import sets remain 124 application and 22 bootloader linker symbols.
The strict GNU link has no undefined symbols and uses 23040 FLASH bytes in the
existing 24576-byte region, leaving 1536 bytes.

The replaced SDK startup unit is removed from composition; the generated vector
unit and C reset unit replace it. Of the prior common units, 775 object hashes
are unchanged. The generated crypto object's hash changes with its build path,
but its source hash, allocated bytes and allocated-section relocations are
identical. Reset imports only the three linker bounds, SystemInit and `_start`.
No constructors/TLS sections are present in the current bootloader objects; no
support for those runtime features is claimed.

R1 source validation passes (778 units, 576 source files, zero excluded units).
Global sources-check still fails on the pre-existing unlisted G2 assembly file.
There is no source qualification, byte-identity claim, device flash or physical
boot proof. Physical clocks/errata, complete DFU activation and application
source completeness remain outstanding.
