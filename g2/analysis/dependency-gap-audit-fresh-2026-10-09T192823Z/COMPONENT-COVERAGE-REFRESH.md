# Six-component coverage refresh — 2026-10-09

No complete source-only build receipt exists for any of the six payloads (0/6). C-compilable byte percentages remain **unknown**, not measured zero. Current reference packaging retains **100% of each original payload**; this does not establish the minimum blob needed by a future source build.

| Component | Stored payload bytes | Verified complete source build | Current retained blob | Raw pseudocode artifact bytes / payload | Byte-validated assembly / payload |
|---|---:|---|---:|---:|---:|
| Apollo main | 3,523,396 | No receipt; C bytes unknown | 100% | 1,555,524 (44.15%) | Unknown |
| Apollo bootloader | 148,599 | No receipt; C bytes unknown | 100% | 112,506 (75.71%) | Unknown |
| Touch | 34,464 | No receipt; C bytes unknown | 100% | 27,879 (80.89%) | Unknown |
| Case | 55,784 | No receipt; C bytes unknown | 100% | 43,072 (77.21%) | Unknown |
| Codec | 326,092 | No receipt; C bytes unknown | 100% | 92,560 (28.38%) | 36,484 (11.19%) |
| EM9305 | 211,948 | No receipt; C bytes unknown | 100% | Unknown | 210,072 (99.11%) |

## Denominators and limitations

Percentages use the six stored payload sizes (total 4,300,283 bytes), including data and headers. They count unique represented ranges, not executable-byte completeness, semantic correctness, independently reviewed pseudocode, or buildable C. Decoded RAM aliases and nested containers are not extra payload bytes. Other assembly percentages are unmeasured despite existing disassembly artifacts.

Raw function-row coverage is a separate metric: Apollo legacy export 7,449/7,449 (100%); bootloader 849/903 (94.02%); touch 308/308 (100%); case 435/435 (100%); five codec exports 929/929 (100%); EM9305 unknown. The larger Apollo partial-range cohort is 8,475 successful outputs among 8,853 envelopes (95.73%); its 1,555,524-byte union cannot be attributed to the smaller legacy cohort. Function rows do not demonstrate whole-firmware coverage.

Codec pseudocode union is 92,560 bytes across five terminal images. Codec assembly is the 36,484-byte A2 XIP image. EM9305 assembly authenticates 210,072 bytes; 816 record-3 bytes and 1,060 other record/metadata bytes are outside that listing. Byte serialization validation does not prove disassembler semantics.

The fresh nine DSP object-section matches total 1,606 bytes (1.96% of stored B2 stage; 0.49% of codec payload). They establish object provenance and are not added to C-build or reviewed-pseudocode coverage. No compiler reproduction or integration receipt accompanies them.

## Supporting receipts

- [Component metrics](COMPONENT-METRICS.json): current payload hashes, manifest retention and historical function rows.
- [Partial range verification](PARTIAL-UNION-VERIFICATION.json): 10,499 envelope hashes, successful nonempty output hashes, unions and complements revalidated.
- [Codec/listing verification](CODEC-LISTING-VERIFICATION.json): 929 codec envelopes and both serialized assembly listings revalidated.
- [DSP independent review](DSP-INDEPENDENT-REVIEW.md) and [verification](DSP-INDEPENDENT-VERIFICATION.json): 37 checks pass; no source compilation claim.
- Current `g2/workflow/state.json`: P2_EXECUTING, G2–G6 not_run. Reviewed pseudocode/freeze/source completeness/byte equality remain separate gates.

All refreshes were offline artifact checks. No sealed runtime test was repeated; no device, source, canonical ledger, Git or production change was made. No access denial occurred. Broader useful source-led research is bounded by the existing static findings, not exhausted by this numerical matrix; DSP caller/table binding remains a concrete static opportunity in the owner track.

## Final FFT binding update

Owner packet `../codec-q15-fft-caller-tables-20261009T193547Z/REPORT.md` binds the selected backup 512-point real FFT/inverse chain, 256-point complex kernels and descriptor layouts. Independent table/archive verification passes five checks: B2 image identity, three exact tables totaling 2,272 bytes, and the explicitly unequal relocated descriptor. See [receipt](FFT-TABLE-INDEPENDENT-VERIFICATION.json). These tables add provenance, not C-compilable coverage or canonical admission; the matrix is unchanged. Live backup use, CPU alias visibility and source compilation remain unproven. The selected DSP caller/table opportunity is now statically resolved within the finite packet scope.
