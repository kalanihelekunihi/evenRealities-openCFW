# Native tensor concatenation in C

`native_model_concatenate.c` implements the six-byte model wrapper at `0x36dcc`
and140-byte shared helper at `0x3f6b4`. The model-vector callback binding now
points to the real C wrapper, which supplies two operands to the shared helper.
Actual C memmove/memcpy providers execute; no assembly, memory-function model,
stock fallback or writable global state is added.

Output batches and first input columns are cached before copying. Each batch
reloads each operand descriptor, rows and data pointer. Word spans and byte
addresses wrap32 bits. Data comes from batch*current span and is appended to a
continuous destination, preserving live descriptor mutations and overlaps.
Output geometry and first columns remain cached even when overwritten.
Zero/negative counts still require valid cache-read descriptors. Zero spans
retain ordinary memmove behavior. The native initial unused spin loop has no
data/output effect and is not retained; timing/interrupt equivalence is unproven.

Verification passes21,224 direct comparisons and6,080 getter/callback
comparisons, including960 using normal build objects. An independent live-memory
oracle checks both native and C executions, including metadata/pointer mutations,
zero and negative counts, four ordinary alias layouts and wrapped dimensions
whose effective spans remain mapped. All58 instruction starts /146 body bytes
execute under32 FP settings. Eight compiled defects are rejected: wrong operand
count/column owner, source batch stride, destination advance, forward-only copy,
reloaded cached batches/columns and reused first-row count.

REA raw-byte/binding reads match the locked image. The current Ghidra session
has no function records at these entries; no fresh pseudocode is claimed.
Actual C getter identity is verified and the callback is called indirectly with
no stock mapping or public-memory normalization.

All927 normal units compile and compose without failures or duplicate strong
symbols. All916 prior nongenerated source/object pairs are unchanged. The normal
provider matches tested sections and decoded symbols after source-file metadata
normalization. Source plan and health-cache layout are unchanged. Application
imports fall73 to72; boot imports remain22.

[Machine-readable evidence](goodix-model-concatenate-c-review.json) pins hashes
and boundaries. Public RAM/full FPSCR, saved registers, SP, masks and R0 are
checked; private stack and caller-clobbered scratch/APSR are outside proof.
Five callback bindings, parent inference, startup and physical hardware remain
open. This composition is not a complete bootable firmware image.
