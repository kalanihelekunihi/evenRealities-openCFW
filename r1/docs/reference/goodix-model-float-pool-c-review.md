# Native float pooling callback in C

`native_model_float_pool.c` implements the260-byte callback at `0x7ca94`.
The alternate-pool executor word relocates to this C function. Existing C
constructors and actual C math execute with no native fallback or algorithm
model. No assembly or writable global state is added.

Configuration bytes are mode/kernel/stride/padding. The routine caches geometry
and traverses output columns before rows, with live forward input reads. Window
ends clip to input columns, but negative starts are retained. Callers must supply
prefix memory; this is the stock address behavior, including preceding-row data.

Max mode starts at -FLT_MAX and calls the native C maximum provider in the
original operand order. Empty windows retain the sentinel. Average mode sums in
binary32 and divides by the actual visited count; empty windows execute0/0,
producing native NaN/FPSCR effects. Other modes leave output unchanged and return0.

Verification passes27,327 direct comparisons and5,434 constructor/callback
comparisons, including858 using normal build objects. All256 pairs of16 special
float encodings run through both max and average under32 FP configurations.
120 independent finite-window oracles use nearest rounding. Six alias layouts,
prefix reads, upper clipping and empty/negative dimensions are checked. All101
instruction starts /260 body bytes execute. Seven compiled defects are rejected:
lower clipping, zero max sentinel, kernel denominator, zero empty-average result,
wrong input/output row strides and invented unsupported mode.

REA raw bytes, constants and binding match the locked image and prior inventory.
The current Ghidra session lacks a function-manager record here; no fresh
pseudocode is claimed. Source constructor replay validates C callback identity
before normalizing only its pointer field for comparison.

All925 normal units compile and compose without failures or duplicate strong
symbols. All914 prior nongenerated source/object pairs are unchanged. The normal
provider matches tested sections and decoded symbols after source-file metadata
normalization. Source plan and health-cache layout remain unchanged. Application
imports fall75 to74; boot imports remain22.

[Machine-readable evidence](goodix-model-float-pool-c-review.json) pins hashes
and boundaries. Public RAM/full FPSCR, saved registers, SP, masks and R0 are
checked; private stack and caller-clobbered scratch/APSR are outside proof.
Seven callback bindings, parent inference, startup and physical hardware remain
open. This composition is not a complete bootable firmware image.
