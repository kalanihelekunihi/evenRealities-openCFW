# R1 powf dispatcher helpers in C

The four private inline-assembly helpers in
`r1/src/application/runtime/native_powf_dispatch.c` now use C sign-bit
operations, a volatile binary32 multiplication, and Arm FPSCR compiler
builtins. This replaces VABS, VNEG, VMUL, and VCMPE/VMRS source expressions
without adding an executable opcode array or trap. The dispatcher outside
those helpers is identical to the recorded baseline.

The [prior probe](powf-dispatch-c-probe.md) pinned that baseline and tested
the exact replacement source against the official R1 application. Re-running
the probe now passes **21,504 stock/C comparisons across 32 FP configurations**
and **4,224 normal-profile comparisons**. They compare scalar results, FPSCR,
public RAM, saved integer/high-FP registers, SP, and interrupt masks. The
production object has the same allocated section bytes and relocations as
the tested normal-profile object. The probe's source SHA-256 matches the
current canonical source. The object container bytes differ, while the
allocated sections and relocations match.

The R1-only build still compiles 975/975 units with no failures or duplicate
strong symbols. The strict bootloader link and vector remain valid. The strict
application link still has **24 undefined functions** and its full flash load
now exceeds the configured span by **29,384 bytes**, 160 more than before.
A source scan drops from 152 to **148 `__asm__` occurrences** and from 39 to
**38 C files** containing assembly. These checks do not establish complete
source-only application linking, byte identity, physical boot, or behavior
outside the replay matrix.
