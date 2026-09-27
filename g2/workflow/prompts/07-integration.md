# P5/P6 integrator: complete source and exact bundle

Operate as the single integration owner on a stable candidate snapshot. Validate
G3/G4 and every accepted unit's corpus, contract, source and toolchain hashes.
Reject stale units. Combine independently reviewed submissions, resolve linkage
and ownership, and generate a source-to-output map covering all executable code,
data/assets and metadata. A later semantic discovery revokes the affected freeze
and parks work; integration may not repair it silently.

Check every linked component, including startup code, runtime libraries,
relocations, symbol placement, section order, fill/alignment, ABI and external
references. No unresolved symbols or retained executable inputs may masquerade
as source completeness. Do not alter the original target pins or patch output
using reference slices. Keep source completeness and exact comparison separate.

After G5, perform two clean builds using only admitted source/assets, source
dependencies, pinned tools and deterministic configuration. Keep original
firmware inaccessible to the builder; a separate comparison stage may read it.
Capture actual build dependencies and source ownership. Reproduce all payloads
and container fields, including ordering, lengths, compression, timestamps,
checksums, padding and any authentication material required by the format.

Compare all six payloads and the whole output by direct byte comparison, size
and SHA-256. On mismatch, report offsets, affected source owners and likely
discriminating experiments. Do not substitute semantic tests, payload-only
equality, a modified build hash, copied signature envelope or two equally wrong
rebuilds for equality to the official artifact.

The final bundle must be 4,301,227 bytes with SHA-256
`f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`.
Require source completeness and clean-input provenance in addition to equality.
Record compiler/signing/asset blockers honestly if the goal cannot yet be met.
Produce build recipes, locks, source ownership, validation and comparison
receipts. Do not claim hardware qualification, sign with a new identity, flash,
publish or release as part of this task.
