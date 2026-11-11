# Native SpO2 transition routines in C

`native_spo2_transition.c` implements the one-channel wrapper at `0x36282`
(52 bytes) and update helper at `0x36c32` (46 bytes). The caller uses a shared
header; its object is unchanged. No new state, allocation or assembly is added.

The helper copies filter classification byte22 to state byte4 before reading
summary flag byte41. Classification0 updates byte5 to the nonzero-flag predicate
and preserves byte6. Classification1 clears byte5 and either clears byte6 or
increments it modulo256. Other classifications preserve bytes5/6. Volatile
accesses retain this ordering when input fields overlap the state record.

## Verification

- 178,266 direct stock/source comparisons also pass independent state oracles.
  They cover every256-by-256 state/flag combination, every counter for states0/1
  with flags0/1/128/255, seven overlap/alignment layouts,32 FP configurations,
  instruction coverage and ten positive defect-witness baselines.
- All S0-S31 and FPSCR remain unchanged. Saved R4-R11, SP, interrupt masks and
  full public RAM are checked;8,192 private stack bytes below incoming SP are
  excluded. FPU system/lazy-stacking configuration is outside that context check.
- Ten compiled defects are rejected: skipped state copy, early quality load,
  modified unknown states, wrong counter/gate reset, signed flags, saturation
  instead of wraparound, wrong filter byte and wrong owner pointer.
- All41 instruction starts /98 native instruction bytes execute.
- 76 constructor-driven streams add3,724 stage/constructor snapshot comparisons,
  912 independent transition oracles and94,848 paired push invocations. Actual
  C heap, constructors, queues, ratio, summary and quality execute through dropout
  and recovery. Twelve streams link from a fresh919-unit normal-build archive.
  Prior filter classification is supplied as an explicit input; the remaining
  filter selector is not implemented by these tests.
- Push calls check saved registers and SP. Full public RAM/FPSCR snapshots are
  after constructors and ratio/summary/quality/transition stages, not every push.

All919 normal units compile and compose without failures or duplicate strong
symbols. Application imports fall83 to82; boot imports remain22.907 unrelated
source/object pairs and the caller object are unchanged. The normal provider's
code, relocations and decoded symbols match the tested object after normalizing
source-file metadata. Source plan and health-cache linker layout are unchanged.

[Machine-readable evidence](goodix-spo2-transition-c-review.json) records hashes,
exact scopes and limits. Physical hardware, timing and interrupt concurrency are
not verified. Unaligned owner tests use the emulator's default access behavior.
Five SpO2 stages remain explicit dependencies, and this relocatable composition
is not a complete bootable image.
