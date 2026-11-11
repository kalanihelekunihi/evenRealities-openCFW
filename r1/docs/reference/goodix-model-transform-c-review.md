# Native tensor stride transform in C

`native_model_transform.c` implements the 92-byte callback at `0x35d12`.
Its executor-address word now relocates to the actual C function. The existing
packed descriptor constructor is unchanged. No assembly, arithmetic on float
payloads, native fallback, or writable global state is added.

The routine caches the input shape, selected strides, output shape and data
pointers. Operation bytes1/2 select from rows*columns, columns and1. Byte0 and
batch count are unused. Signed output bounds preserve empty/negative cases.
Forward word reads and writes preserve live aliases, signaling NaN bits,
subnormals and signed zeros without changing FPSCR. Valid selectors are0..2;
no behavior is invented for native out-of-table stack accesses.

Verification passes 17,894 direct comparisons, including six positive defect
baselines, and 2,052 constructor/callback comparisons.324 constructor pairs use
normal build objects. An independent address-space oracle checks live memory
for both native and C executions. All nine selector pairs, six overlap layouts,
32 FP modes and all33 instruction starts /92 native body bytes are exercised.
Six compiled defects are rejected: swapped stride, omitted row stride, wrong
output indexing, abbreviated source indexing, reversed writes and arithmetic
on float payloads. Constructor replay verifies actual C callback identity and
normalizes only its relocated pointer word after execution.

All923 normal units compile and compose without failures or duplicate strong
symbols. All912 prior nongenerated source/object pairs are unchanged. The normal
provider matches tested sections and decoded symbols after source-file metadata
normalization. Application imports fall77 to76; boot imports remain22. Source
plan and health-cache layout are unchanged.

[Machine-readable evidence](goodix-model-transform-c-review.json) pins hashes
and boundaries. Public RAM/full FPSCR, saved registers, SP, masks and R0 are
checked; private stack and caller-clobbered scratch/APSR remain outside proof.
Nine callback bindings, parent inference, final startup and physical hardware
remain open. This composition is not a complete bootable firmware image.
