# OpenCFW change scan — 2026-10-08 22:25 UTC

Compared with the [21:28 scan](../rescan-2026-10-08T212840Z/REPORT.md), component C/header/assembly inventory grew **630 → 650 files: 20 added, none modified or removed**. All 650 are in the Git index; none matches an ignore rule. Counts include historical implementations, headers and partial helpers, and do not measure firmware completeness.

## New source and knowledge

| Batch | Recorded validation | Main result |
|---|---:|---|
| [Trim initialization](../audio-trim-initialization-closure-2026-10-08/REPORT.md) | 1,310 comparisons | Variant/factory-date predicates and once-only original-trim capture |
| [Common startup](../audio-common-startup-closure-2026-10-08/REPORT.md) | 3,784 comparisons | Retention/TON/LP startup suffix, callback wrappers and PCM2.2 reset |
| [Clock reset gates](../audio-clock-reset-gates-2026-10-08/REPORT.md) | 392 comparisons | Retained request flags are reset even when active recovery is skipped |
| [Active clock reset](../audio-clock-reset-active-2026-10-08/REPORT.md) | 1,392 comparisons | Complete recovery and common initializer control flows; actual original providers execute |
| [GPIO/clock requests](../audio-gpio-providers-2026-10-08/REPORT.md) | 2,432 comparisons + 10 original-only assertions | Full GPIO configuration and cached request ownership; caller error-discard paths |
| [INFO1/memory/oscillator source](../../components/audio/info_memory_offline/) | Unsealed intermediate results | Four new complete helper bodies; final combined-build validation remains pending |

These are author-recorded comparisons under explicit synthetic state, not tests rerun by this scan. Suites can overlap and should not be summed as distinct coverage.

The new evidence separates retained clock flags from cached request ownership: reset consumes retained flags while cached request bytes can survive and later republish a request. GPIO configuration rejects unsupported drive modes; selected callers discard that error. Clock recovery can continue through readiness failures, so return success does not prove physical readiness.

## Unfinished validation discovered

The INFO1/memory/oscillator batch is **not sealed**. INFO1 (96), memory (664) and composed initializer (38) report PASS against ELF `12280f5bd42daf79816e503e21e27454887f597895e2c7577777782a68e1b5af`. Oscillator (384) reports PASS against a different ELF, `4a81046ae3ddb64e443d3e9c6ab9c71bdad34fa09ed6a49ae76ecd47d97a89cc`. These individual results do not establish one validated final combined build. The immediate completion step is to rerun the first three suites against the final build, verify source/receipt identities, and seal that batch. This scan preserved the work rather than rerunning or changing it.

## Preservation and visibility

All **2,187 hash entries across inspected dictionary-form analysis/component seals**, **110 audit inputs**, and **four candidate checkpoints** match their recorded hashes. This seal scope is broader than the preceding scan; the difference is not a count of newly produced artifacts. List-form manifests are outside this verification scope.

HEAD changed from `36ff5930a4e832156f9ee3111e83480756ebef37` to `36337d9b39ff36d318b0531f2968ca7e0554a7b1` (Add G2 offline reconstructions and validation evidence). The current working changes are 18 staged files in the unfinished INFO1/memory batch. Existing staging was preserved. Source ignore inspection returned zero matches: **gitignore is not hiding the new source**. Registered worktrees/global-exclude settings are captured in the snapshot.

Physical calibration, real power/clock settling, live scheduler/IRQ state, resident-ROM dependencies and full M55 behavior remain limits. No complete source-built or byte-identical OTA is established. Only this new scan report/snapshot were written in the checkout; no generator, behavioral suite or firmware operation was run.

[Exact source delta, hashes, Git state, checkpoint verification and result identities](snapshot.json).
