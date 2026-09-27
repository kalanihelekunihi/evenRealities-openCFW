# Preparation record — 2026-09-26

Scope: repository organization and procedure/prompt design only. No firmware
decompilation, C reconstruction, firmware build, hardware action, or campaign
worker dispatch was performed. Review agents inspected the process and prompt
design; an implementation agent helped retire the old launcher.

## Repository changes

- Added the current procedure under `g2/workflow/`, with a target lock,
  preparation state, evidence contracts, generic record templates, and prompts
  for GPT 6 Luna with low reasoning.
- Added root `AGENTS.md` and updated navigation/methodology to make the new
  order explicit: whole-artifact pseudocode, independent review and freeze,
  then C decomposition and source reconstruction.
- Moved the old driver prompt and September 12 workflow review into
  `docs/archive/g2-incremental/`. Their original bytes are preserved; former
  paths now redirect to the current procedure.
- Marked `remaining-work.md` as a historical queue without changing its table
  rows. `remaining-work.json` and its existing staged changes were preserved.
- Retired execution and mutation commands in `continue-analysis.sh` and the
  supervisor CLI. Read-only historical diagnostics remain available. There is
  no automatic switch back to incremental reconstruction.

The checkout began with 473 tracked paths carrying staged or unstaged changes.
Existing firmware sources, overlays, manifests, dependency checkouts, payloads
and authenticated corpora were retained in place. No reset, clean, stage,
commit, submodule update, broad re-pin or scratch-directory deletion was used.
The preexisting Git index remained byte-for-byte unchanged during validation.

A local preparation baseline and validation receipt are retained under the
ignored `build/workflow-reset-2026-09-26/`. They record the initial status/index
fingerprint and copies of changed navigation documents. This is a preparation
audit, not a backup of the entire repository or a corpus freeze.

## Target identity checks

The official manifest and blob provenance identify `s200_v2.2.6.10`,
4,301,227 bytes, SHA-256
`f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`.
All six local extracted payloads matched their recorded sizes and SHA-256 values.
The existing cached reference package at
`g2/build/reference/package/g2-openCFW-s200_v2.2.6.10.evenota.bin` also matched
that whole-bundle size/hash. It was read, not rebuilt. This cache path must be
reauthenticated and preserved durably when the campaign starts.

The old work queue and hybrid release pins name different output hashes. They
are not the target. The repository's `2.2.6.12` release describes custom firmware
derived from official `2.2.6.10`, not a separately authenticated official target.

Existing corpora are leads, not proof of the new gate. For example, Apollo
function counts vary by corpus, and a historical Makefile comment and old
runner description disagree about a bootloader harvest whose expected directory
was absent during this inspection. P1 must verify files, hashes and scope.

## Verification and remaining execution work

- 28 focused tests passed: historical prompt/session/dependency regressions and
  six isolated launcher-retirement checks. Retirement checks use temporary
  fixtures and verify blocked commands do not create state or invoke providers.
- Shell syntax and whitespace/diff checks passed.
- Target/state/template JSON, local workflow links, target fingerprints,
  archived document identity, unchanged queue rows and unchanged Git index
  were checked.
- Firmware builds and broad firmware tests were not run; firmware sources were
  not changed by this preparation.

All new phase gates remain `not_run`. No actual analysis or C assignments exist.
The prompt pack and procedure specify a future dispatcher, coverage validators
and immutable freeze process; those tools are not implemented here. After the
user requests the next stage, the coordinator starts at P1, verifies the whole
artifact, implements and checks campaign validation, and only then dispatches
bounded analysis tasks. C planning remains closed until all six payloads pass
the full-corpus freeze gate.
