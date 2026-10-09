# Touch compiler matrix acceptance checks

[TOUCH-TARGET-CONTROLS.json](TOUCH-TARGET-CONTROLS.json) independently fixes target slices. Strip the 32-byte wrapper and use flash base 0x3300. Capture is `[0x8FA0,0x8FD0)` / payload `[0x5CC0,0x5CF0)` (48 bytes), Configure `[0x8FD0,0x9178)` / payload `[0x5CF0,0x5E98)` (424), ConfigureScan `[0x9178,0x9218)` / payload `[0x5E98,0x5F38)` (160). Their hashes are recorded in that file and peers agree with sealed attribution receipts.

Acceptance checklist:

- Authenticate full official target before slicing. Preserve exact sizes and full-section hashes; equality requires all bytes and equal lengths. Mismatch lists over only minimum length must be accompanied by length delta so truncation is not overlooked.
- For these three bodies require no nonempty REL/RELA relocation section targeting the code section. Do not mask branch offsets, literals or instruction bytes to admit an exact match. Relocation-normalized similarity is a separate result. Check ELF architecture/endian mode and section identity.
- Compare Capture and ConfigureScan from the same compilation as Configure, using unmodified PDL pin/source and device/header environment. Both are existing exact controls, not newly recovered functions. A Configure match with failed peers is weaker than a consistent three-body match.
- Preserve compiler executable/archive identities, version text, container digest/platform, exact argv, flags/includes, return codes, preprocessed `.i`, assembly `.s`, dependency file and object/output hashes. Read-only mounts support source immutability; compare consumed PDL/header hashes to pinned baseline and capture before/after hashes for host inputs.
- Compare preprocessed inputs meaningfully across releases: compiler builtin headers can differ legitimately; PDL/config/type definitions should be invariant or differences explained. A new compiler/header environment is not strictly a one-variable compiler-version experiment.
- Keep candidate acquisition failures distinct from byte mismatches. Do not rerun existing 13.3 screens. Seal complete candidate outputs and bind reviewer hashes before ledger promotion.

Outcome interpretation: matching all three selects a compatible candidate, not the authenticated producing compiler/source. Multiple matches leave a version interval. Same 24-byte mismatch across candidates weakens compiler-version-only explanation within this tested environment. Different mismatch narrows code-generation behavior without proving a source patch. A match only after source/macro changes is a different hypothesis and must not be represented as unchanged upstream attribution.

## Preliminary review of owner script

The currently available `touch-compiler-matrix-2026-10-09/matrix.py` pins source hash, uses immutable container digest and read-only tool/PDL/header mounts, preserves preprocessed/assembly/dependency/object files, requires no relocations and compares full section bytes against all three fixed controls. These are appropriate safeguards. It writes results progressively; a partial list is not a completed matrix.

Before accepting final receipts, require full target hash assertion (script currently slices without authenticating it), actual argv/exit-code recording, explicit target hashes and length delta, and source/header immutability against baseline. Consumed hashes exist but a comparison to prior header hashes still needs review. At this snapshot no acquisition/results receipt was present for assessment; script existence does not establish execution or success. This audit did not execute it or access its temporary inputs.
