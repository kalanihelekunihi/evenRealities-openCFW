# Repository work instructions

## G2 workflow reset — 2026-09-26

The current G2 process is [g2/workflow/README.md](g2/workflow/README.md).
It supersedes earlier decompilation, incremental overlay, source-only queue,
and agent-continuation instructions. Historical evidence remains useful;
historical instructions are not the current work plan. The cross-device plan
(including R1, which now also targets a byte-identical rebuild) is
[docs/roadmap.md](docs/roadmap.md); for G2, the workflow procedure governs.

The present assignment is preparation only. Do not start decompilation,
firmware reconstruction, or agent jobs from the new prompt pack until the user
requests that next stage. A later request to begin decompilation authorizes
that stage, not an early C implementation stage.

For subsequent G2 work, complete and independently review pseudocode for the
entire locked firmware artifact, then freeze the corpus. Only after that gate
may C implementation chunks, shared interfaces, and their task dependency graph
be defined. Do not recycle the removed `remaining-work.*` queue (Git history) as the new queue. Use GPT 6 Luna
(`gpt-6-luna`) with reasoning effort `low` for the parallel workers.

The final target is a complete build from source whose bundle is byte-identical
to the locked official artifact. A changed reference hash, retained executable
blob, opcode array, trap, or merely equivalent replacement cannot satisfy it.
Keep pseudocode coverage, source completeness, and byte equality separate.

Preserve existing staged and unstaged work. Do not reset, clean, re-pin, move
authenticated evidence, or change firmware sources as part of preparation.
The old launcher and queue were removed on 2026-09-29 (recoverable from Git
history). Look up facts in the consolidated references first:
`docs/hardware/`, `docs/tooling.md`, `g2/docs/reference/`, `g2/symbols/`,
`g2/config-recovered/`, `r1/docs/*.md`, and `r1/config-recovered/`. See the
procedure for output ownership, evidence, and gates.
