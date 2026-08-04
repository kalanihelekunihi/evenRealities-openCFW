# Nanopb varint32-pair pre-promotion regression baseline

Status: executable Task 0 boundary captured before either varint32 candidate
source file exists. This document records test debt; it does not accept that debt
as correct firmware behavior.

## Revision and scope boundary

The authenticated predecessor revision is
`b6260d5f4c24ccb9fd2a1334780a01880ff19c42`. Task 0 began at reviewed
plan-only descendant `4abb9c10935c244e365fd4d3ebc911a960a20e5b`.

Before the first Task 0 edit:

- `git merge-base --is-ancestor b6260d5f... HEAD` returned zero;
- the worktree was clean;
- `git diff --name-only b6260d5f...HEAD` contained only
  `docs/superpowers/plans/2026-08-02-nanopb-decode-varint32-pair-production-promotion.md`;
- `git diff --check b6260d5f...HEAD` passed; and
- no source, fixture, overlay, manifest, provenance, signing, flashing, reset,
  boot, or hardware operation was performed.

## Historical discovery evidence and stable replacement

The completed predecessor discovery log
`build/source/unittest-discover-s-tests-final-b6260d5f.log` was copied under a
tranche-specific name and independently verified as 365,726 bytes / SHA-256
`fdb4342d9ea4f97995d87a774f6e29124c3b469e0e6af43373ebe2f8ee942134`
before the Apple rebuild. It records `Ran 2615 tests in 1530.074s`, 58
failures, 12 skips, and zero errors.

`make source` atomically recreates `build/source`; consequently, an ignored log
copied inside that generated directory is not durable across the required rebuild.
That operation removed both the original and its first copy. No attempt was made to
reconstruct or misrepresent the historical bytes. All Task 0 logs after that finding
were written directly to ignored `build/baselines/`, outside the recreated directory.

The fresh reproducible supporting pre-promotion run is:

```text
python3 -m unittest discover -s tests -v
```

Its stable log is
`build/baselines/varint32-task0-4abb9c10-full-discovery.log`: 366,005 bytes /
SHA-256
`6c22440df5ca4a2238f9c920652872e6afee5b46ebeb8d056b00484055b12124`.
It records `Ran 2617 tests in 1510.296s`, 58 failures, 12 skips, and zero
errors; exit status 1 is expected for the pinned failures. The two additional tests
are the new identity-boundary guards.

The durable authority is the deterministic normalized evidence at
`docs/research/nanopb-decode-varint32-pair-regression-evidence.json`: 28,762
bytes / SHA-256
`1300c8544b5ef5d7bb775ec5b25f93367f5312a10793dfaba1471855e0d0f417`.
It is committed and therefore available in a clean checkout without the ignored
supporting log. Its closed version-2 schema records the source log's byte size,
SHA-256, and command status; the `Ran` and `FAILED` totals; all 58 failure
identities including subtest suffixes; each delimiter-structured result block and
body SHA-256; zero error records; and all 12 nullable raw skip identities,
nonempty resolved identities, exact reasons, line SHA-256 values, and resolution
provenance. The complete raw traceback and assertion-message bytes remain
authenticated by both the per-result digests and the supporting full-log hash. The
historical message bodies remain authenticated by the predecessor log's distinct
size and SHA-256.

The single anonymous raw skip line contains only
`skipped 'real signed-varint mutation builds require linux-clang'`. Its identity is
resolved by the committed 866-byte resolver map at
`docs/research/nanopb-decode-varint32-pair-skip-resolvers.json`, SHA-256
`7b4a2c774d61096e74048111d77f81db385afb4b395cfff3f10c6e3fad95108b`.
That closed version-2 map authenticates the exact Task 0 baseline commit
`4abb9c10935c244e365fd4d3ebc911a960a20e5b`, its source path, Git blob
`6b93a951c6c0be881a7758b8da729163f765bf52`, test class, and source
SHA-256 used to derive
`setUpClass (test_runtime_nanopb_decode_svarint_production.NanopbDecodeSvarintLinuxBuildMutationTests)`.
The resolver reads those content-addressed historical bytes from Git and rejects
missing history, a non-commit revision, a changed path-to-blob binding, a non-blob
object, or a changed content hash. It intentionally ignores the mutable HEAD
worktree copy, whose later test additions have a different SHA-256.
Within the authenticated source, the resolver also requires one uniquely selected
top-level class and one exact synchronous `@classmethod setUpClass(cls)` hook. The
module's direct `import unittest` binding must be unique and unshadowed, and that
hook's non-nested method body must contain exactly one
`raise unittest.SkipTest(<exact reason string literal>)` with no extra arguments or
keywords. A matching string elsewhere in the file, class, another method, or a
nested function, class, or lambda is not provenance.
The other eleven skips carry their verbatim unittest identity with provenance method
`raw_unittest_output`. All twelve resolved identities must be nonempty and unique.

`tools/unittest_identity_baseline.py` separately validates the normalized schema
and the raw unittest capture. This comparison of the durable evidence with the fresh
log completed with status zero:

```text
python3 tools/unittest_identity_baseline.py \
  --skip-resolvers \
  docs/research/nanopb-decode-varint32-pair-skip-resolvers.json \
  docs/research/nanopb-decode-varint32-pair-regression-evidence.json \
  build/baselines/varint32-task0-4abb9c10-full-discovery.log
```

Independent set-difference inspection recorded:

```text
baseline failures: 58
current failures: 58
new failures: []
missing failures: []
current errors: []
```

The raw parser accepts only real 70-character delimiter-structured result blocks,
requires exactly one non-vacuous `Ran` trailer and exactly one final `OK` or
`FAILED` summary, reconciles failure/error/skip counts, validates an appended
`command_status` when present, and rejects duplicate identities. Aggregate test
counts alone are deliberately not the regression authority. Every later full run
must add no failure or error identity relative to the normalized evidence. Resolving
the owned varint32 missing-source identity is expected.

## Exact skip inventory (12)

1. `test_apollo_overlay_relocated_closures.ApolloOverlayRelocatedClosureTests.test_prel_movwt_pair_matches_lld_rel_oracle` — `ld.lld is unavailable`.
2. `setUpClass (test_runtime_nanopb_decode_svarint_production.NanopbDecodeSvarintLinuxBuildMutationTests)` — `real signed-varint mutation builds require linux-clang`.
3. `test_runtime_nanopb_decode_svarint_production.NanopbDecodeSvarintProductionTests.test_deterministic_linux_target_object_and_relocation_closure` — `exact Linux target-object gate requires linux-clang`.
4. `test_runtime_tlsf.RuntimeTlsfTests.test_wasm32_ilp32_allocator_oracle_compiles_links_and_runs` — compatible `wasm-ld` is unavailable.
5. `test_thumb_branch_audit.ShippedImageAuditTests.test_even_ai_hook_is_installed_over_the_stock_prologue` — reviewed CFW bundle not supplied.
6. `test_thumb_branch_audit.ShippedImageAuditTests.test_image_is_the_pinned_reviewed_build` — reviewed CFW bundle not supplied.
7. `test_thumb_branch_audit.ShippedImageAuditTests.test_only_the_even_ai_trampoline_is_defective` — reviewed CFW bundle not supplied.
8. `test_thumb_branch_audit.ShippedImageAuditTests.test_trampoline_fixture_matches_the_image` — reviewed CFW bundle not supplied.
9. `test_toolchain_profiles.LinuxProfileReproductionTests.test_canonical_profile_rejects_non_apple_clang` — alternate profile unavailable on Apple.
10. `test_toolchain_profiles.LinuxProfileReproductionTests.test_overlay_reproduces_committed_pins_and_is_deterministic` — alternate profile unavailable on Apple.
11. `test_toolchain_profiles.LinuxProfileReproductionTests.test_ring_source_package_reproduces_committed_profile_pin` — alternate profile unavailable on Apple.
12. `test_toolchain_profiles.SourceProfileReproductionTests.test_core_source_package_reproduces_committed_profile_pin` — alternate profile unavailable on Apple.

## Separately owned orphan RED

The command
`python3 -m unittest -v tests/test_runtime_nanopb_decode_varint32_candidate.py`
runs one test and exits 1. Its sole failure is
`tests.test_runtime_nanopb_decode_varint32_candidate.NanopbDecodeVarint32CandidateTests.test_candidate_sources_exist`.
The first failing assertion remains `self.assertTrue(SOURCE.is_file())` at line 18,
with `AssertionError: False is not true`, because
`components/shared/nanopb/runtime_nanopb_decode_varint32_candidate.c` is absent.

The stable orphan log is 801 bytes / SHA-256
`0e87146e9728b40c261a1a120dfac24c3f32cf88d0d07fb2b10e9ac3d74df686`.

## Command and log boundary

All logs below are ignored output under `build/baselines/`. Their final
`command_status` line is part of the stated size and hash.

| Command | Status | Log bytes | Log SHA-256 |
|---|---:|---:|---|
| `./make.sh source` | 0 | 3,395 | `bae636ba22b6771bad41ff7337203f76fbb89c8b1e0f058d8e2c043d5050ddd0` |
| `./make.sh verify` | 0 | 49,529 | `a76c331d7e879b20a58bc138e5f756b7377a1e6521c5a6b43a1e1d1638c515f9` |
| `make vendor-snapshots` | 0 | 2,435 | `6f93ff188df91fe56059e25b3db03986753d307564dbcdd898811703b0d7c863` |
| focused current nanopb + profile + boundary suite | 0 | 10,441 | `b3492ba606c3ec5d3376bb5731c345db3c287458cde1dff8df8d637e0829cef1` |
| `python3 -m unittest -v tests/test_toolchain_profiles.py` | 0 | 4,066 | `889aca06287a464fe0bf8e5fcb7b22756c280844a4ee3178baacb5cea118b7d2` |
| orphan candidate test | 1 (expected) | 801 | `0e87146e9728b40c261a1a120dfac24c3f32cf88d0d07fb2b10e9ac3d74df686` |
| full discovery | 1 (expected) | 366,005 | `6c22440df5ca4a2238f9c920652872e6afee5b46ebeb8d056b00484055b12124` |

The focused command ran the nanopb snapshot, private read-pair, stream constructor,
signed-varint production, complete toolchain-profile, and new identity-boundary test
files. It ran 77 tests in 21.010 seconds and passed with six expected Apple-host
skips. The dedicated profile run ran 32 tests in 0.123 seconds and passed with four
expected skips.

## Compiler and artifact identities

The build selected profile `apple-clang` and `/usr/bin/clang`, whose reviewed first
version line is `Apple clang version 21.0.0 (clang-2100.3.27.1)`.

The source rebuild reproduced the predecessor artifacts exactly:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 124,970 | `1cfdeb0382a10f1c9dad9d203bd2f3a0d1f56390815eafffcf925f7731bb80ec` |
| Apollo-main component | 3,648,366 | `eaf24d1adce80ce958c5ff90585bc2da6a2f76634a9d2539e3a5cf2b37814bf1` |
| source package | 4,426,860 | `e77b984d3644cade761b2aecec399ccb9249c419c2ca6e9f4963cbbbfa208cf7` |
| flash plan | 734,550 | `a14dc76800b140af67678fe7d6b86d92152aeb2a9e523467c84afbe19653e24e` |
| package build report | 2,323 | `8b49f17724accbecd568e046a940868980d28d845d0bb9222fb42a49d9f03b7f` |

## RED to GREEN evidence

The first execution of `tests/test_unittest_identity_baseline.py` failed during
import with `ModuleNotFoundError: No module named 'unittest_identity_baseline'`.
The quality-hardening RED added captures for empty, truncated, vacuous,
missing-summary, contradictory-summary/status, fake-heading, and duplicate-heading
logs. Those tests initially failed because the permissive helper exposed no
structured raw parser or normalized-evidence validator. The final 14-test boundary
suite covers clean `OK`, ordinary `FAILED`, skip-only, subtest, duplicate identity,
and appended `command_status` cases, plus rejection of a synthetic new failure and
new error. Its skip-resolution checks distinguish nullable raw identities from
required resolved identities, reject missing, null, or mutated resolution and
provenance fields, and authenticate the source-backed resolver map. It also
authenticates the normalized evidence
without requiring ignored output, while optionally checking the supporting raw log
when locally present. All 14 tests pass.

The post-resolution focused current nanopb, profile, and boundary run passed all 89
tests with the same six expected Apple-host skips. The separately owned candidate
test still produces only its expected missing-source failure.

No signing, flashing, reset, boot, or G2 hardware operation was performed.
