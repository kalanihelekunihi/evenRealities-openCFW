# Corpus provenance

This corpus is the reverse-engineering and decompilation evidence behind the G2
analyzers under [`../../tools`](../../tools). It was produced on a Threadripper
workstation named `lorelei` and returned to the repository on 2026-08-08 as a
single 12,684,322-byte bundle with SHA-256
`8e721a0b4fe872081f92d49a5393422b323cd077ae66e8c1badc083c7b8c240b`.

That bundle is no longer stored compressed, and the host name is no longer part
of the layout. The evidence is unpacked and filed by subject. Nothing was
rewritten: every file is byte-for-byte what the bundle contained, and the
embedded `SHA256SUMS` manifests still authenticate it in place.

## Original delivery roots

The bundle arrived as twenty `mktemp`-suffixed scratch roots. They map to the
current layout as follows, with the tree hashes recorded at delivery time:

| Delivery root | Files | Tree SHA-256 | Now at |
| --- | ---: | --- | --- |
| `opencfw-apollo64-return.3LC1Dq` | 400 | `8672a71f…` | `apollo-main/ghidra/` |
| `opencfw-em9305-ghidra16-return.9S8jMH` | 35 | `dca7d372…` | `em9305/ghidra/round16-initial/` |
| `opencfw-em9305-ghidra16-return2.hrpTGF` | 35 | `dca7d372…` | *dropped — byte-identical to the above* |
| `opencfw-em9305-ghidra16-current-return.9sHgcz` | 35 | `5f7a957d…` | `em9305/ghidra/round16-current/` |
| `opencfw-em9305-ghidra16-targeted-return.OstnD2` | 35 | `93b85316…` | `em9305/ghidra/round16-targeted/` |
| `opencfw-em9305-ghidra16-authoritative-return.dqmDy6` | 36 | `eed0bf76…` | `em9305/ghidra/round16-authoritative/` |
| `opencfw-em9305-ghidra-residual-round2-return.SvoSIJ` | 36 | `9b33bbfc…` | `em9305/ghidra/residual-round2/` |
| `opencfw-em9305-ghidra-residual-round3-return.B1XMm7` | 36 | `55cb741f…` | `em9305/ghidra/residual-round3/` |
| `opencfw-em9305-ghidra-residual-round4-return.xU4j4s` | 36 | `2a11401a…` | `em9305/ghidra/residual-round4/` |
| `opencfw-em9305-sdk-round2-return.4mZWiA` | 68 | `3fb8f393…` | `em9305/sdk-comparison/round2/` |
| `opencfw-em9305-sdk-round2-min8-return.DIdndF` | 68 | `6e0109c9…` | `em9305/sdk-comparison/round2-min8/` |
| `opencfw-em9305-sdk-batch16-return.BDdHwx` | 36 | `ef42b2e9…` | `em9305/sdk-comparison/batch16/` |
| `opencfw-em9305-sdk-batch16-min16-return.XNpW2a` | 36 | `cd1e4799…` | `em9305/sdk-comparison/batch16-min16/` |
| `opencfw-em9305-sdk-fast-enforced-return.bz1xdX` | 6 | `c4454485…` | `em9305/sdk-comparison/fast-enforced/` |
| `opencfw-wsf-matrix-return.Q1ui1J` | 2 | `3a12ecf5…` | `wsf/matrix-v2/` |
| `opencfw-wsf-matrix-return.tHXgCw` | 46 | `3e8d2a90…` | *merged — same artifact, already unpacked* |
| `opencfw-wsf-current11-return.9ABvyY` | 2 | `9f90abdc…` | `wsf/current11/` |
| `opencfw-wsf-current11-return-v2.mvcPuA` | 5 | `e8d8f8bb…` | `wsf/current11-v2/` |
| `opencfw-wsf-os-readiness-return.4bGhzQ` | 2 | `a86c61dc…` | `wsf/os-queue-readiness/` |
| `opencfw-lorelei-compact-return.Jx9UKx` | 60 | `ee8a9cef…` | split by subject; see below |

The compact root was a mixed lane delivery. Its subtrees went to their subject
homes — `em9305/nop-aware/`, `em9305/size-delta/`, `iar/`, `qpc/`,
`source-lanes/`, and `wsf/stock11-inspect/` — which is exactly where its own
manifest already addressed them, so [`SHA256SUMS.lane-bundle`](SHA256SUMS.lane-bundle)
verifies unchanged from the corpus root.

## Changes made when unpacking

Three, all recorded:

1. **Decompressed.** The outer bundle, the twenty-four per-topic readiness
   artifacts, and four nested archives were extracted. No `.tar.gz` remains.
2. **Deduplicated.** `ghidra16-return2` was byte-identical to `ghidra16-return`
   and the two `wsf-matrix-return` roots carried the same artifact; one copy of
   each is kept.
3. **Excluded.** Three CPython bytecode caches were dropped:
   `em9305/size-delta/__pycache__/{analyze_em9305_sdk_discovery,compare_em9305_modified_sdk_functions,compare_em9305_sdk_archive}.cpython-314.pyc`.
   They are regenerable caches of scripts stored beside them. They remain listed
   in `SHA256SUMS.lane-bundle`, and
   [`../../tools/verify_research_corpus.py`](../../tools/verify_research_corpus.py)
   treats exactly those three as known exclusions; any other missing file fails
   the check.

Compiled object files (`iar/math-errno/*.o`, `wsf/current11*/**/*.o`) were
**kept**. They are the measured artifacts of the compiler-matrix comparisons,
not build leftovers, and the signed manifests cover them.

## Verifying

```sh
make -C g2 research-corpus
```

This authenticates every file against the embedded `SHA256SUMS` manifests and
against the repository-level [`../MANIFEST.sha256`](../MANIFEST.sha256).
