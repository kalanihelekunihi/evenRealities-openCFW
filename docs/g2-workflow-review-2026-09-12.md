# G2 reverse engineering workflow review — 2026-09-12

Scope: process review of the current working tree and local continuation artifacts. No decompilation, firmware changes, builds, runner launches, or hardware operations were performed. Existing staged and unstaged work was left intact. Findings describe this snapshot, including uncommitted runner improvements; they are not claims about every historical session.

## Main finding

The highest-value improvement is to turn existing evidence into selective, durable work state. The repository already has extensive decompilation, provenance, upstream attribution, tests, dependency records, and session resumption. Adding more unstructured logs or repeatedly invoking the same gates will not close the remaining integration and semantic gaps.

### Evidence sampled

| Observation | Repository evidence | Implication |
| --- | --- | --- |
| Progress and goal documents are 809,294 and 578,838 bytes, respectively (13,334 and 9,239 lines). | `g2/docs/progress.md`, `g2/docs/source-only-goal.md` | Keep the stable goal separate from session history; load a compact current view and only relevant evidence. |
| Local runner logs contain 696 files totaling 198,777,885 bytes; 158 saved prompts total 1,948,940 bytes. | `build/continue-analysis/{logs,prompts}` | Raw history is already retained. The missing leverage is indexed retrieval and concise resumable knowledge. |
| 95 archived result snapshots include 92 partial and three done results. These are snapshots, not independent tasks or a success-rate denominator. | `build/continue-analysis/logs/*.result.json` | Separate useful incremental progress from repeated blocked verification before judging efficiency. |
| AM-040 has 21 snapshots; its latest three repeat 64 reviewed leaves, passing tests, and LC3 LLD/littlefs integration blockers. | AM-040 result snapshots dated 2026-09-12 at 02:31:10, 03:11:08, and 03:50:42 | Requeue when relevant prerequisite fingerprints change, not merely because the previous status was partial. |
| CD-001 has 22 snapshots, but recent snapshots advance source-owned byte counts. | CD-001 result snapshots at the same three timestamps | Do not suppress productive partial work with a blanket retry limit. Track measurable deltas. |
| XC-002 repeatedly checks ledgers while other lanes change inputs. | XC-002 snapshots, including 03:50:42 | Batch integration and ledger refreshes around a stable input snapshot. |

Counts are point-in-time filesystem observations. No elapsed-time or token instrumentation was analyzed, so no speedup percentage is claimed. A compact saved prompt can still cause a large context read: the largest observed prompt was 22,725 bytes, and the rendered instructions also direct workers to the goal document's completion section.

## Prioritized improvements

1. **Make retries dependency- and evidence-driven.** Extend the existing deferred records rather than introducing another queue. `tools/continue_analysis_dependencies.py` already preserves blockers, prerequisites, remaining segments, and verification-only work; `continue-analysis.sh:cmd_ingest` maps partial results back to todo unless dependencies block them. Represent toolchain/configuration/integration blockers with stable keys and relevant input hashes, including blockers without a work-item ID. An unchanged blocked checkpoint should not trigger another full verification attempt. Allow useful independent segments to continue. Detect dependency cycles and unresolved IDs explicitly.

2. **Save provider-independent knowledge throughout a session.** `tools/continue_analysis_session.py` persists session IDs and usage-limit checkpoints, but its resume instruction is generic. Its non-usage-limit exit path removes the session checkpoint; a result file is requested at completion, which may be too late after a crash or timeout. Add an atomic per-item checkpoint after each evidence decision or completed segment, before expensive builds, and before yielding. Preserve facts, uncertainty, failed approaches, exact next action, artifact hashes, and current processes/lock state. Raw logs and provider history remain supporting evidence. Test restoration into a fresh session with no prior chat context.

3. **Use stable structured state and generated views.** Current rendering includes the Markdown row, including accumulating notes, plus deferred progress. Regeneration carries status by item ID and displayed range; those alone do not establish unchanged semantic scope. Give each item an input/scope fingerprint covering component, image digest, address space, body range sets, and dependency identities. Keep an append-only attempt history and one compact current checkpoint. Generate status tables and summaries from that state. Migrate existing records with backups and validation; do not silently replace the runner's current writer contract.

4. **Separate recovery, verification, and integration.** The runner already has an integration lock and recommends private build outputs. Preserve these protections, but avoid repeatedly forcing every otherwise-complete leaf through a shared failing build. Produce a candidate receipt in private outputs; integrate a compatible batch against a captured snapshot; then run the required component/package gates and refresh shared pins once. A failed shared gate leaves the item integration-pending, never done. Shared Makefile/document mutations also need coordinated ownership; rereading immediately before editing does not by itself prevent concurrent lost updates.

5. **Make C maintainability an explicit milestone.** CD-001 snapshots show productive byte-exact assembly recovery. That is valuable evidence, but it is not automatically progress toward readable C. Track reviewed C, justified ABI assembly, exact-byte reconstruction, data generators, and retained content separately. Require an explanation for assembly and a C follow-up where exact encoding is the only reason for it. Work by coherent ABI/data-flow clusters where possible, rather than treating every address fragment as an independent software module.

6. **Resolve the invariant hierarchy.** `docs/methodology.md` describes byte identity as G2's invariant, while the active source-only goal distinguishes the hybrid build, experimental reconstruction, and future source-only completion. Publish one short authoritative contract: preserve the reference profile's guarantees; recover semantics and interfaces for maintainable source; validate intentional divergences explicitly; keep software integration, hardware qualification, and redistribution status separate. Do not let historical exact-placement goals dictate all future C design or relax existing gates without a reviewed change.

7. **Reuse analysis incrementally with correct invalidation.** The harvest already uses analyzed Ghidra projects, `-noanalysis`, worker copies, and hashes; the transparent database already reconciles multiple evidence sources and preserves split body ranges. Build on these. Index symbols, callers/callees, data references, types, upstream matches, and negative findings. Cache exports and narrow validation by input image, analysis-project revision, processor specification, scripts, compiler/flags, headers, source and dependency hashes. A function's byte hash alone is insufficient when types or callee prototypes change. Measure project-copy/startup cost before changing shard counts or concurrency.

8. **Strengthen reusable semantic validation.** Keep provenance and hash gates, but distinguish them from behavioral evidence. Prefer reusable architecture-aware oracle harnesses covering calling conventions, widths, signedness, aliasing, volatile accesses, state transitions, error paths, and MMIO event order. Avoid a test whose expected behavior is generated solely from the candidate being tested. Share harness machinery across related leaves while retaining per-function evidence and license boundaries. Inspect ELF ownership, relocations, entry redirects, and retained calls before production admission.

## Proposed rollout and acceptance criteria

- First: capture a baseline of duplicate no-change attempts, time spent in context loading/builds/lock waits, and useful closures per session. Normalize by subsystem difficulty; do not optimize raw function counts.
- Next: add compact checkpoints and input-bound receipts to the existing runner. Verify atomic writes, interrupted-session recovery, stale-checkpoint invalidation, and fresh-session handoff.
- Then: add prerequisite-change scheduling. Reproduce the AM-040 blocked scenario: an unchanged blocker causes no rebuild; a changed relevant prerequisite queues completion verification exactly once.
- Finally: introduce a single integration owner per batch and selective caches. Compare clean and cached output digests, deliberately invalidate a header/type/toolchain dependency, and run the required gates on integrated changes.

Suggested primary metric: unique stock ranges newly backed by reviewed, production-routed source per unit of effort, reported separately from compiled output size. Also track semantic closures, candidate age, unresolved ABI assumptions, duplicate attempts, cache reuse, and rebuild/lock time. Deduplicate overlapping ranges; preserve separate component/address-space identities. Never equate zero unclassified bytes, compilability, or a passing package checksum with functional firmware.

The accompanying [reusable prompt](g2-reconstruction-driver-prompt.md) specifies this future workflow. It is a proposed replacement for the current work instruction, not an installed runner change.
