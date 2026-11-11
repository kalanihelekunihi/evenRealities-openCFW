# Native SpO2 quality and logistic routines in C

`native_spo2_quality.c` implements the native quality routine at `0x88e80`
(518 bytes) and its logistic helper at `0x3efd8` (54 bytes). The normal build
now resolves `r1_goodix_spo2_quality`. A shared header gives its existing caller
the native uint32 return type; the caller object remains unchanged.

The quality routine preserves signed-byte correlation, the unsigned comparison
of the sign-extended summary count, readiness/metric flags and descriptor mask.
It stores byte41 before loading the score inputs, keeping the native cached
record pointer when that store overlaps the summary pointer. Metric tests use
ordered GT, whereas the logistic slope selection also takes the upper slope on
unordered comparisons. Raw signed clamps and the -1 sentinel remain explicit.

Scoring executes the actual C expf and encoded software-double providers.
Weights are0.4,0.4,0.2, with a binary32 boundary after each contribution and the
initial positive-zero addition retained. The final raw signed clamp and unsigned
RTZ conversion use the verified C integer helper. The new unit adds no assembly,
algorithm models, executable arrays or writable allocated sections. Source
executions have no stock code mapped; some existing math dependencies still
contain arithmetic assembly.

## Verification

- 48,160 stock/source routine comparisons:4,096 mixed/special cases,10,240
  flag/alias cases,31,040 direct logistic cases,1,440 finite score cases and1,344
  coverage cases. Mixed, alias and logistic checks cover all32 FP configurations.
- Full FPSCR, public RAM outside an8,192-byte private stack range, saved
  R4-R11/S16-S31, SP and interrupt masks match. Quality returns R0=0; direct
  logistic tests compare S0. Source code and math/data providers are real C
  implementations rather than boundary models.
- Independent checks cover all64 flag combinations under32 configurations,
  another1,440 finite-input flag results,1,437 finite weighted scores, and256
  logistic values. Three score cases within0.001 of an integer boundary are
  excluded only from the mathematical score oracle, retaining exact stock
  comparison. The logistic oracle's absolute tolerance is2e-5.
- Seven compiled defects are rejected: signed summary comparison, unordered
  metric acceptance, ignored mask, unsigned correlation, wrong weight, unsigned
  raw clamp and reloading the pointer after an overlapping flag store.
- Code hooks execute all170 instruction starts /572 body bytes reported by REA.
  This is instruction coverage, not exhaustive path coverage.
- All917 normal units compile and compose without failures or duplicate strong
  symbols. Application imports fall85 to84; boot imports remain22.905 unrelated
  source/object pairs and the typed caller object are unchanged. The normal
  quality and math objects match tested sections, relocations and decoded symbols
  after normalizing source-file metadata. Source plan and cache layout are unchanged.

[Machine-readable evidence](goodix-spo2-quality-c-review.json) records hashes,
exact test scopes and build outputs. REA dossier limitations include reuse of its
local analysis snapshot. Physical sensors, interrupt concurrency and full
firmware startup remain untested. Seven SpO2 stages remain explicit imports;
summary is the next dependency. The composed image is not bootable firmware.
