# Native inference input helpers in C

`native_spo2_infer_support.c` implements normalization at `0x95750` (198 bytes)
and tensor initialization at `0x5d5d0` (16 bytes). These are native dependencies
for the remaining inference implementation. The parent `r1_goodix_spo2_infer`,
generated graph/subgraph and operator callbacks remain open; they are not replaced
with models or successful stubs.

Normalization retains the native comparisons and FP status, including apparently
redundant sign comparisons. It caps the maximum at binary32 `0x3ca3d70a` and clears
below `0x33d6bf95`. Exact lower equality is normalized. NaN/unordered branches,
flush behavior, forward overlap and live loads match stock. C division and the
actual source EABI clear provider execute. Tensor words are element size, batches,
rows, columns and data pointer; native R0 returns the data pointer.

## Verification

- 33,328 direct routine comparisons cover32 FP configurations, special encodings,
  scalar/pair/random vectors, exact thresholds, in-place and both directional
  aliases, tensor data in caller stack, raw zero/high-bit words, instruction
  coverage and nine positive defect-witness baselines.
- Independent oracles check672 finite normalized vectors and3,520 tensor records
  and returns. Mathematical normalization oracles use nearest rounding; all modes
  retain exact native comparisons.
- Nine compiled defects are rejected, including wrong cap/lower equality,
  magnitude, NaN handling, omitted comparison status, output traversal, descriptor
  field order and return pointer.
- All214 native body bytes execute. Public RAM and full FPSCR, saved R4-R11/
  S16-S31, SP and interrupt masks match. Only8,192 private stack bytes below
  incoming SP are excluded; tensor R0 is compared explicitly.
- Twenty-four real-constructor streams add1,752 constructor/stage snapshots and
  29,952 paired push invocations. Existing C processing supplies rolling input to
  normalization and a native-layout tensor.576 independent tensor/range checks
  pass. Eight streams use a fresh920-unit normal-build archive.
- Per-push checks cover saved registers/SP. Full RAM/FPSCR comparisons are at
  constructor and stage boundaries, not after each push. Prior classification is
  an explicit input; the neural model is not executed or simulated.

All920 units compile and compose without failures or duplicate strong symbols.
All909 prior nongenerated source/object pairs are unchanged. Imports remain82
application /22 boot. The normal provider matches tested code/relocation sections
and decoded symbols after normalizing source-file metadata. Source plan and
health-cache linker layout are unchanged. No new assembly or writable allocated
sections are introduced.

[Machine-readable evidence](goodix-spo2-infer-support-c-review.json) records hashes
and proof limits. Physical hardware and interrupt concurrency remain untested.
Five SpO2 stages remain unresolved, including inference; this is not a complete
bootable firmware image.
