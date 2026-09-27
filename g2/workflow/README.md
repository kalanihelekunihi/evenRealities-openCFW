# G2: whole-firmware pseudocode, then source reconstruction

Status: **P1 inventory executing** in campaign `20260926T223240Z`. The G1
target-and-inventory gate remains blocked pending component evidence and
independent reviews. Current receipts and blockers are recorded in
`g2/build/pseudocode-first/20260926T223240Z/inventory/status.json` and
`blockers.json`. This directory is the active G2 procedure as of 2026-09-26;
it replaces the incremental reconstruction workflow. Existing firmware
sources and historical evidence are preserved.

The sequence is fixed:

1. Authenticate the exact official bundle and inventory all of its contents.
2. Recover and review pseudocode for every executable region across all six
   payloads; account for every non-code byte and all nested images.
3. Independently verify completeness and freeze the entire corpus.
4. Derive C modules, shared contracts, and parallel implementation assignments
   from that frozen corpus.
5. Rebuild every payload and the outer bundle from source, and prove exact
   equality to the original artifact.

P1 inventory and independent-review tasks have been dispatched using bounded
contracts and hash-pinned evidence. P2 remains gated on G1; no C implementation
task may start before G3/G4. The prepared prompt pack is guidance, not a general
job launcher.

| Start here | Purpose |
| --- | --- |
| [PROCEDURE.md](PROCEDURE.md) | stages, hard gates, and exact completion criteria |
| [CONTRACTS.md](CONTRACTS.md) | records, coverage accounting, handoffs, and freeze rules |
| [REPOSITORY.md](REPOSITORY.md) | active versus historical paths and future output layout |
| [prompts/README.md](prompts/README.md) | how to compose the GPT 6 Luna Low prompts |
| [target.json](target.json) | immutable intended artifact and six payload identities |
| [state.json](state.json) | current campaign phase and gate state |
| [templates/](templates/) | unfilled task, result, and freeze record examples |
| [PREPARATION.md](PREPARATION.md) | what was inspected, reorganized, and verified in this reset |

The identified target is the official `s200_v2.2.6.10` EVENOTA bundle,
4,301,227 bytes, SHA-256
`f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`.
The original manifest and provenance agree on that identity. Historical hybrid
output hashes, release pins, and the old work queue are different records and
must not redefine this target. See `target.json` for local verification status.

“Full firmware” here means the entire identified OTA artifact, including all
nested programs, assets, metadata, and padding. Resident ROM or factory images
absent from the artifact must be recorded as external dependencies; they must
not silently disappear from the behavioral model or be claimed as recovered.
