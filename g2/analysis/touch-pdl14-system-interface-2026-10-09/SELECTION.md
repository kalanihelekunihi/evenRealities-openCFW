# Predeclared authentic system-interface correction

Rerun only cy_sysint.c, cy_syslib.c and cy_systick.c from the failed finite
census. Unchanged compiler/source/flags/device macro; add a first include path
containing unchanged official Infineon TARGET_CY8CKIT-040T system_cat2.h at
commit d1bf634023bf92d083ad0e32083987f67b4a64e6, SHA-256
5eb47d11872c01221d27a5b8be87327fc564aafdd1fb6fde2eea2421161ecf99.
This replaces the minimal system shim for these three units only. It supplies
actual public ISR/delay/vector declarations; no invented prototype, mutable
runtime table, executable implementation or frequency value is inserted.

The selected device remains CY8C4046FNI_T412, Cortex-M0+/Thumb, -Og and prior
freestanding/no-builtin/function-sections configuration. A PSoC4000T board
reference is compatible declaration evidence, not exact producer/BSP identity.
All12historical targets are retained; keep every success/mismatch/relocation or
missing-section result. Preserve original compile failures rather than rewriting
them. No linking of globals to guessed firmware addresses.
