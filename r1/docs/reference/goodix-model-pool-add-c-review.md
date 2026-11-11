# Native model pooling and float-add callbacks in C

`native_model_pool_add.c` implements pooling at `0x41816` (434 bytes) and
float addition/activation at `0x98edc` (164 bytes). Two formerly opaque executor
address bindings now resolve to actual C functions. Existing descriptor
constructors are unchanged and emit callable C addresses through normal relocations.
No assembly, opcode arrays, native fallback or writable state is added.

Pooling uses signed bytes. Max2 preserves the eight-load/four-store group and
full final unroll, including native writes beyond a partial logical row; buffers
must be padded. Max4 and average3 preserve cached dimensions and stride. Average3
retains division, sign comparison, half adjustment and defined RTZ conversion,
including the inexact flag on zero. Unsupported mode/kernel pairs remain native
no-ops returning0.

Float addition finishes its sum pass before reading activation. It processes
rows*columns, as native does. ReLU/leaky branches preserve carry/unordered behavior,
signed zeros and NaN operand selection. Leaky slope is reloaded for each ordered
negative output, so operation/output overlaps follow the native mutations.

## Verification

- 45,312 direct comparisons:512 smoke,31,232 full-mode matrix,12,832 alias,
  208 independent mathematical cases,518 instruction-coverage cases and ten
  positive defect-witness baselines. Exact cases cover32 FP configurations.
- 2,167 constructor/callback comparisons execute actual C constructors and
  indirect calls to the C callbacks.342 use normal921-unit build objects.
  Actual C pointer identity is verified before normalizing only the two relocated
  callback words for measurement. Source replay has no stock code mapped.
- Independent signed pooling oracles cover all32 FP modes. Finite float-add and
  activation oracles use nearest rounding; exact native replay covers every mode.
- Eleven compiled defects are rejected: signedness, grouped loads, partial tail,
  integer average, zero-round bypass, add operand order, unordered ReLU, cached
  slope, zero leaky activation, invented pool mode and wrong callback binding.
- All219 instruction starts /598 native body bytes execute. Public RAM, full
  FPSCR, saved R4-R11/S16-S31, SP, interrupt masks and R0 match;8,192 private
  stack bytes below incoming SP are excluded.

All921 normal units compile and compose without failures or duplicate strong
symbols. Application imports fall82 to80; boot imports remain22. All910 prior
nongenerated source/object pairs are unchanged. The normal provider matches
probed sections, relocations and decoded symbols after normalizing source-file
metadata. Source plan and health-cache layout remain unchanged.

[Machine-readable evidence](goodix-model-pool-add-c-review.json) records hashes
and exact limits. Nine other callback bindings and the inference graph remain
open. The missing Ghidra function record at vector callback `0x30534` is documented
with raw disassembly for later work. Physical hardware, concurrency and complete
startup are untested; this is not a complete bootable firmware image.
