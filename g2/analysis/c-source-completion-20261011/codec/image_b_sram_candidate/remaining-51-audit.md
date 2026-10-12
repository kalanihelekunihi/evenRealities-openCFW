# Image-B remaining address frontier after 162-unit receipt

This is an address-suffix census against all 288 Ghidra catalogue entries,
not a whole-body equivalence result. Current source names cover 237 entries;
three of those are clock data, not callable bodies. Fifty-one remain outside.

* 32 lie in the `0x1000fb14..0x1001283c` software binary64 runtime. The
  selected C-SKY archive already contains pinned LLVM compiler-rt sources for
  binary64 add, subtract, multiply, divide, comparison and conversion, plus
  unsigned 64-bit division. Native entries including `0x10011de4`,
  `0x10011e14`, `0x10011e50`, `0x10012050`, `0x100121a0`, `0x100121e0`,
  `0x10012220` and `0x10012398` show matching operation roles in the retained
  decompilation. These are **semantic alias candidates**, not 32 missing
  source claims or proved exact stock equivalence. Floating exception and
  rounding effects remain genuine imports.
* `0x10003144` is the BSS bound literal and `0x10004c78` is a callback/literal
  boundary. Both are decompiler catalogue entries, not missing callables.
* `0x10004880` is a compact-IRQ C-SKY entry requiring an authentic assembler
  path; the current compiler accepts ordinary C-SKY but has not assembled its
  compact interrupt form.
* Four entries `0x10008aa0..0x10008e20` form the native formatter chain.
  They are already source-owned in selected `backup_runtime_printf.c`, which
  includes the exact pinned NationalChip `utility/libc/printf.c` implementation.
  The native flag bits match upstream `FLAGS_LEFT`, `FLAGS_HASH`,
  `FLAGS_UPPERCASE` and `FLAGS_PRECISION`; the 32-byte digit buffers and
  32/64-bit numeric conversion call graph also match. These four are address
  crosswalk omissions, not newly missing C bodies. Exact compiled/native
  formatter output over the full caller corpus remains a qualification task.
* Twelve other callable leads cover IMCRA/denoise application setup, native
  DSP/FPU paths, and a larger platform path at `0x10015d34`. The native
  `0x1000e94c` decompiler loses a live float register and cannot be reduced
  from the pseudocode's apparent zero value. `0x1000d46c` hits a bad-data
  edge; direct ISA analysis is required.

Native `0x1000c5d0` executes `divu r20,r19,r1` before its explicit zero
check whenever the high dividend word is at least the divisor. For divisor
zero this first instruction already has architecture-specific behavior; the
only observed caller supplies 1024. The C source is therefore qualified for
nonzero divisors, not a made-up divide-by-zero policy.

The eight unresolved link imports are the two final BSS linker bounds, two
external product/IMCRA configuration objects, two FP-environment helpers,
the native address-zero word read and an invalid UART port's ambient
direction. Their source or layout contracts must be established separately
from the address census.
