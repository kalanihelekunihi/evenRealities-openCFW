# Record templates

These files are deliberately unfilled. `template_only: true` must cause the
future dispatcher/validator to reject them. A coordinator creates separate
campaign records with `template_only: false`, filled required fields and actual
input hashes. Do not edit these examples into global completion receipts.

| Template | Use |
| --- | --- |
| [task.json](task.json) | one bounded analysis, review, planning or reconstruction assignment |
| [result.json](result.json) | one immutable worker attempt and handoff |
| [freeze.json](freeze.json) | coordinator's global G3 receipt after independent review |

Allowed task phases: `inventory`, `pseudocode`, `review`, `freeze_review`,
`partition`, `c_reconstruction`, `integration`. `UNASSIGNED` is invalid for
execution. `partition`, `c_reconstruction` and `integration` require G3;
the latter two also require G4. Analysis/review tasks require their applicable
upstream gate and submission receipts. Required fields depend on phase; a
missing corpus hash is expected before freeze and invalid for post-freeze work.

Populate repeated fields consistently:

- `ranges`: `{ "image_id": "...", "address_space": "...",
  "file_start": 0, "file_end_exclusive": 16, "load_start": 4096,
  "isa_mode": "..." }`. These numbers demonstrate the shape only, not G2 facts.
  Include separate records for discontiguous bodies and linked parent mappings.
- `input_files` / `artifacts`: `{ "path": "...", "sha256": "...", "role": "..." }`.
  `input_files` hashes must describe actual working-tree contents.
- `required_gate_receipts`: `{ "gate": "G1_TARGET_AND_INVENTORY",
  "path": "...", "sha256": "..." }`, referencing validated evidence.
- `validation_receipts`: paths/hashes of records with actual `argv`, `cwd`, input
  and tool hashes, `exit_code`, output hashes and tested scope.
- `blockers`: `{ "id": "...", "range_or_scope": "...", "reason": "...",
  "prerequisite": "...", "wake_condition": "..." }`.
- `component_summaries`: one record for each of the six target component IDs,
  with total/accounted/code/reviewed-code/unknown byte counts, body/review counts,
  unresolved semantics and coverage/review receipt paths and hashes.

Result statuses are `ready_for_review`, `partial`, `blocked`, `stale_input`.
`null` is not a status and `ready_for_review` is not coordinator acceptance.
Freeze decisions are `pass` or `blocked`; `not_evaluated` never opens G3.
Immutable invalidations are separate records referring to a freeze ID/hash;
the coordinator's gate registry must check them before every dispatch/resume.

See [CONTRACTS.md](../CONTRACTS.md) for function, data, ledger and receipt record
requirements. These examples are not JSON Schema files and do not implement
schema, coverage, or gate enforcement.
