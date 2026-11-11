# R1 motion-detection stream, sampling and ring accumulation in C

`native_motion_detection.c` supplies detection stream setup `0x493c8`, its
sample callback `0x491d0`, and ring accumulation `0x94a60`. The
[review receipt](motion-detection-c-review.json) binds production source/object
hashes, REA bytes/literals, differential fixtures, native cold initialization,
negative controls, qualification and normal composition.

Setup clears the 48-byte state and registers `acc`/`detect` at rate 1, flags 0,
returning the raw registration word. It leaves the independent log counter alone.
The callback reads the count byte at offset 180 before its null branch, preserving
the stock null fault. Counts below 20 return; counts above 25 are locally capped.
It examines up to five samples at stride count/5, scales signed axes by 1/1024,
computes magnitude using the existing C square-root provider, and accepts absolute
magnitude deviations below 5 using the stock integer bit comparison. Accepted
deviations are averaged and smoothed as 0.7*new + 0.3*old, with contraction disabled
to preserve stock rounding stages. It pushes the ring, reloads the smoothed value
for classification, increments the wrapping log counter, logs/reset at 600 and
sets the pending byte. Classification and log mutations are observed through
fresh state reads.

Ring accumulation preserves unchecked index address arithmetic, overwrite/subtract
ordering, the fresh sum reload, and fresh index/count reads after a write that may
alias control fields. A C-only probe failed on two NaNs because the compiler
commuted addition and selected a different payload. The final source retains one
ordered `VADD` boundary for ARM NaN precedence. Native `VCVT.s32.f32` is also retained
for log values, where an ordinary C cast cannot guarantee out-of-range/NaN behavior
and FPSCR effects. These are two arithmetic instructions, not a retained detector
assembly body. The higher-level state, sampling and registration flow is C.

The fixture passes 1,699 paired stock/C cases with FPSCR comparison. It executes
the actual C square-root provider and ring arithmetic, modeling classification,
registration, clearing and logs. Cases cover count-byte boundaries, signed axes,
sampling stride, rounding/FZ/DN modes, nonfinite/subnormal smoothing history,
ring saturation and control-field aliases, counter wrap, changing log modes and
classifier/log mutations. Eight compiled defects are rejected: halfword count,
wrong stride, wrong smoothing, stale ring index, reset counter during setup,
unordered addition, rounded log conversion and lost pending flag. Public state,
provider arguments and logical faults are compared; callee-saved registers, SP,
masks and FPSCR are checked. Only setup R0 is compared; caller-clobbered registers,
APSR and private stack residue are excluded. Physical/concurrent behavior remains
unverified.

The cleared state occupies 48 bytes at `0x2001e480`; the separate counter is two
bytes at `0x20006eec`. Stock RW/ZI handlers execute on poisoned memory with guards,
and an independent RW decoder confirms all 50 bytes start at zero. No surrounding
state is claimed. Final source-only RAM placement remains unproven.

All 637 units compile and both relocatable compositions pass without duplicate
strong symbols. All 636 earlier objects remain identical. Detection setup is
resolved and classifier `0x94c74` is exposed as a typed native dependency, leaving
application/bootloader import counts at 172/34. Manifest checks pass. None of the
three roots qualifies as exact. The source plan remains at 4,339 source-built
bytes; a fresh hybrid matches the locked artifact with 641,821 executable
pull-through bytes and 248 resource bytes. Complete source-only linking and
firmware hardware validation remain unfinished.
