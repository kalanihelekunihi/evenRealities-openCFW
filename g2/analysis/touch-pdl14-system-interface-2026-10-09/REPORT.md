# Authentic PSoC4000T system-interface correction

The three finite-census translation units now compile unchanged using the
official system header instead of the earlier minimal shim. All12predeclared
targets are retained: nine have relocation/extent boundaries, and three named
sections are absent (DelayCycles, EnterCriticalSection, ExitCriticalSection).
No exact raw code-only section is promoted and no executable stub was invented.

Official Infineon TARGET_CY8CKIT-040T system_cat2.h was acquired at detached
commit d1bf634023bf92d083ad0e32083987f67b4a64e6; SHA-256
5eb47d11872c01221d27a5b8be87327fc564aafdd1fb6fde2eea2421161ecf99,
Apache-2.0. `acquisition.json` pins URL/content. It supplies cy_israddress,
delay-global declarations and vector-table declarations with real public types.
It inserts no runtime definitions/values. PSoC4000T family compatibility does
not establish the exact producing BSP or its current master revision.

`SELECTION.md` and `selection.json` predeclare this single environment change
and the12targets before compilation. Compiler/device/flags/source remain the
same authenticated GNU14.2.1, CY8C4046FNI_T412, Cortex-M0+/Thumb/-Og configuration.
The new include directory precedes the prior minimal shim; all original files
and failure receipts remain untouched. `results.json` preserves actual argv,
diagnostics, every consumed input and output hash, target lengths/differences,
and relocation names/types/offsets.

Remaining emitted-function work is original-address-bound linkage and literal
accounting, notably named delay/vector/global relocations. No guessed global
address was supplied. The absent functions need their genuine inline/assembly
emission/source contract; a missing named section is not missing firmware code.
No further header changes are justified by the successful compilations.

The fixed historical census has54entries:25independently reviewed functions
and29remaining (23relocation/extent boundaries, five absent named source-unit
sections, one separate inline candidate). The reviewed aggregate is2368bytes,
including the independently reviewed nine finite-census literal extents and
two SysTick extents. New SysInt/assembly/delay successors are separately
review-pending; do not count them as reviewed or campaign-admitted. This is a
finite work list, not global source exhaustion.

Approved Docker runs used read-only tool/source/header/interface mounts,
task-only writable output, no network/capabilities and no-new-privileges.
No production/device/Git/campaign state changed. Independent interface review
passed in `../coverage-audit-parallel-2026-10-09/SYSTEM-INTERFACE-REVIEW.md`.

Independent discovery cross-check: system_cat2.h from official
TARGET_CY8CPROTO-040T pin3f680f7660f7dbf16d4e75c4f57b24a3c030cb54 is byte-identical
to this task's official TARGET_CY8CKIT-040T header (sameSHA-256 above). Its
system/startup definitions add provenance, not linked executable substitutes.
The authenticated T412 device macro remained unchanged; neither BSP package
selection, board pins nor linker configuration was imported.
