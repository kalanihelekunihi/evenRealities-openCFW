# Where work belongs

The new workflow has one entry point, [README.md](README.md). It keeps current
process instructions separate from old evidence and generated work.

| Location | Role after the reset |
| --- | --- |
| `AGENTS.md` | current G2 stage ordering and preparation scope |
| `g2/workflow/` | active procedure, target, preparation state, prompts and templates |
| `docs/archive/g2-incremental/`, `remaining-work.*`, `continue-analysis.sh`, `tools/continue_analysis_*.py` | removed 2026-09-29; recoverable from Git history (last present in `832137ec`) |
| `build/continue-analysis/` | old local logs/checkpoints, if present; never resume into the new campaign |
| `g2/docs/reference/`, `g2/symbols/`, `g2/config-recovered/` | consolidated reference facts, naming seeds and recovered upstream configuration (added 2026-09-29) |
| `docs/hardware/`, `docs/tooling.md`, `tools/bootstrap/` | cross-device hardware reference, tooling guide and pinned tool installer |
| `g2/research/` | retained Ghidra corpus (Apollo main, case, EM9305, IAR, QP/C), reusable only after identity and scope validation |
| `g2/manifests/`, `g2/tools/`, `g2/tests/` | reference manifest, container analyzers and Ghidra pipeline with their tests; the hybrid overlay tree was removed 2026-09-29 |
| `g2/blobs/official/g2-2.2.6.10/` | existing extracted oracle payloads and provenance |
| `g2/build/pseudocode-first/<campaign>/` | future local analysis attempts, projects and frozen campaign artifacts |
| `r1/`, `third-party/` | R1 decompilation corpus and references; submodule and archive dependency pins (the old `g2/third_party/` snapshots were replaced by submodules on 2026-09-29) |

Suggested future campaign layout (not populated by this reset):

```text
g2/build/pseudocode-first/<campaign>/
  identity.json
  inventory/       images.jsonl, coverage.jsonl, data.jsonl, interfaces.jsonl
  raw/             immutable exports and tool diagnostics per image
  reviewed/        pseudocode and function records per image
  reviews/         independent reviews and global reconciliation
  receipts/        executed tools and evidence fingerprints
  projects/        private decompiler projects; never shared writable
  attempts/<task>/<attempt>/
  tasks/           analysis tasks first; C tasks only after G3
  results/         immutable result/checkpoint records
  frozen/<version>/ corpus index, SHA256SUMS, freeze.json
  contracts/       only created after G3
  reconstruction/ only created after G3/G4 as appropriate
  comparisons/     component and bundle comparisons after source builds
```

`g2/build/` is ignored local working storage, not the only long-term copy of
accepted evidence. Before relying on a freeze for C work, preserve its complete
content and manifest in a versioned, backed-up evidence location recorded in
the freeze receipt. That location must survive build cleanup. Admit reviewed
evidence into a dedicated versioned repository location only after explicitly
updating the relevant evidence index; do not insert files into the existing
hash-pinned `g2/research/` corpus casually.

Paths that the workflow pins by hash (`g2/tools/open_cfw.py`, the analyzers, the
case and EM9305 manifests and `research/corpus/case/ghidra/final-frontier/`) are
kept in place because tooling and evidence checks refer to their exact paths and bytes. Moving them now would
mix a workflow reset with a large re-pin and could damage unfinished work.
Scratch/build directories may contain unique unfinished outputs; do not delete
them based only on their names. Future cleanup should inventory usage and retain
recoverable copies before removal. Preparation did not run `git clean`, a build
clean target, a reset, submodule updates, or firmware builds.
