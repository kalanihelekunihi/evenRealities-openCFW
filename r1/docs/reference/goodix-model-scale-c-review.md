# Native scalar/vector multiplication callback in C

`native_model_scale.c` implements the 152-byte callback at `0x95b20`.
The tail-vector executor word now relocates to its C function. The actual C
getter and an indirect call execute that function. No assembly, native fallback,
algorithm model or writable global state is added.

The scalar branch tests wrapped second rows+columns==3, reads one weight even
for an empty first tensor, and caches that scalar across writes. It processes
first rows*columns. Otherwise second rows==1 enables vector multiplication:
outer rows and row stride are cached, but every inner condition reloads the
second descriptor pointer/column count. Other shapes are no-ops returning0.
Source-first multiplication, forward overlaps and native FPSCR effects remain.

REA raw-byte reads match the locked application. Getter literal `0x74aa0`
contains Thumb callback `0x95b21`; Capstone decodes53 instructions ending with
POP PC. Ghidra has no function-manager record at this entry; no recovered
pseudocode is claimed.

Verification passes21,383 direct comparisons and4,864 getter/callback
comparisons, including768 using normal build objects. All256 pairs of16 special
float encodings run through both multiplication paths under32 FP modes.96
independent finite numerical cases, four ordinary alias layouts and32 targeted
live-bound descriptor overlaps pass. All152 body bytes execute. Seven compiled
defects are rejected: invented scalar/unsupported modes, wrong row stride,
cached live bound, reloaded scalar, swapped NaN operands and omitted multiply.

All924 normal units compile and compose without failures or duplicate strong
symbols. All913 prior nongenerated source/object pairs are unchanged; the normal
provider matches tested sections and decoded symbols after source-file metadata
normalization. Source plan and health-cache layout remain unchanged. Application
imports fall76 to75; boot imports remain22.

[Machine-readable evidence](goodix-model-scale-c-review.json) pins hashes and
boundaries. Public RAM/full FPSCR, saved registers, SP, masks and R0 are checked;
private stack and caller-clobbered scratch/APSR are outside proof. Eight callback
bindings, inference, startup and physical hardware remain open. This composition
is not a complete bootable firmware image.
