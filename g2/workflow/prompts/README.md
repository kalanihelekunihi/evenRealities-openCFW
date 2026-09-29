# Prompt pack for GPT 6 Luna Low

These are prepared instructions, not jobs already launched. Begin with
[00-coordinator.md](00-coordinator.md) only when the user requests the next
stage. The coordinator must fill and validate a task contract before dispatch.

Set the actual worker model to **`gpt-6-luna`**, reasoning effort **`low`** in
the execution tool. Writing the model name in a prompt does not configure it.
Use fresh, bounded worker contexts and the concurrency available to the
environment; do not resume old reconstruction conversations. There is no new
launcher in this directory. The retired `continue-analysis.sh` launcher has
been removed and must not be restored to run these prompts.

For each worker, send these items in this order:

1. [common.md](common.md).
2. Exactly one phase prompt below.
3. A fully populated [task contract](../templates/task.json) plus its hash-pinned
   evidence packet. Include the needed excerpts and precise file paths; do not
   ask a worker to read the entire repository or historical progress log.

| Prompt | Allowed stage and deliverable |
| --- | --- |
| [01-inventory.md](01-inventory.md) | P1: authenticate and map assigned container/image scope |
| [02-pseudocode.md](02-pseudocode.md) | P2 after G1: raw and reviewed-candidate pseudocode with evidence |
| [03-review.md](03-review.md) | P2/P3: independent review of one immutable analysis submission |
| [04-freeze.md](04-freeze.md) | P3: independently check global completeness; propose freeze decision |
| [05-partition.md](05-partition.md) | P4 **only after G3**: derive C ownership, contracts and task DAG |
| [06-c-reconstruction.md](06-c-reconstruction.md) | P5 **only after G3 and G4**: implement one C/data unit |
| [07-integration.md](07-integration.md) | P5/P6 **only after G3/G4**: serial integration and exact rebuild proof |

Every dispatch verifies required gates from actual receipts, hashes and
validator results. **05–07 are dormant until the whole artifact is frozen.**
There are no instantiated C chunks in this preparation. Pseudocode analysis
assignments are independent coverage ranges; they must not fix future module
boundaries prematurely.

For Luna Low, prefer one complex function or a handful of small related bodies
with the necessary caller/callee context. Give explicit interpretations already
proved by shared evidence, examples of the expected record shape, and one clear
acceptance checklist. Keep mandatory evidence complete; reduce scope when it
does not fit. Start with two workers and one independent review stream as
capacity permits; scale only after checking submission quality and collisions.
The coordinator owns global state and does not become another competing writer.

The pack intentionally excludes auto-commit, permission-bypass flags, automatic
provider fallback, and automatic model/effort changes. Unknown semantics become
an explicit analysis task or blocker. They never become plausible filler C.
