# Native softmax and shared math arithmetic in C

`native_model_softmax.c` implements the152-byte callback at `0x5d244` and
resolves its executor binding to a real C function. `native_expf_tanhf.c` now
has no inline assembly: nine arithmetic expressions are replaced by C. Existing
coefficients/tables and the shared integer-conversion header remain unchanged.
No writable state, native fallback or algorithm model is added.

Softmax uses output rows as count and preserves three live passes: ordered max
selection, exponentiation/sum/store, then reload/division. Its88 clamp compares
signed raw float bits after VMOV; the decompiler cast is not an actual numeric
conversion. Sum operand order and overlapping buffers remain native. REA dossier,
raw bytes, literals and callback binding agree with the locked image.

C arithmetic retains rounded multiply then accumulator-first addition. VMLS
uses bit-negated product followed by addition, preserving native NaN sign and
operand priority. Signed integer-to-float conversion is explicit; absolute and
negation manipulate sign bits without arithmetic FP exceptions. Noinline volatile
helpers prevent unwanted expression contraction under the tested profile.

Verification passes25,359 softmax routine/getter comparisons and eight compiled
defect controls. Both the prior and new math providers execute in source-only
replay; all256 pairs of16 special logits are tested under32 FP modes with the
new arithmetic provider. Seven independent finite oracles pass. All50 native
instruction starts /152 body bytes execute.4,096 getter pairs use normal build
objects and explicitly link the newly compiled math provider.

Math verification passes689,664 primitive instruction/C comparisons,264,960
expf/tanhf regressions against the prior source, and132,480 stock expf comparisons.
Six compiled defects are rejected, including plain subtract for VMLS, reordered
NaN operands, unsigned conversion and arithmetic absolute/negation. Primitive
checks cover full FPSCR, raw result, saved registers and SP with no writable
sections/imports. Full routine checks also cover public RAM and interrupt masks.
Tanhf uses the prior source reference; stock expf executes at `0x38f08`.

All926 normal units compile and compose without failures or duplicate strong
symbols. All914 unrelated nongenerated source/object pairs are unchanged; the
existing math provider changes intentionally. Both normal providers match probed
sections and decoded symbols after source-file metadata normalization. Math table
bytes, source plan and health-cache layout remain unchanged. Application imports
fall74 to73; boot imports remain22.

[Machine-readable evidence](goodix-softmax-arithmetic-c-review.json) pins hashes
and proof limits. Private8192-byte stack frames and caller-clobbered scratch/APSR
remain outside full routine proof. Other firmware units still contain assembly,
including raw ABI bridges. Six callback bindings, parent inference, startup and
physical hardware remain open. This is not a complete bootable firmware image.
