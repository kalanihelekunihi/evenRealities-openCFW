# Nanopb `pb_skip_string` pre-promotion regression baseline

Status: independently sealed Apple- and Linux-profile Task 0 boundary captured
before the production `pb_skip_string` source promotion.

This document records existing test debt; it does not classify that debt as
correct firmware behavior. The promotion may remove an identity that it owns,
but must add no failure or error identity on either reviewed profile. Focused
candidate, current-package, manifest, provenance, and artifact gates must be
green.

## Revision and scope boundary

The production promotion base is
`7e78e38e4401bc095cca266e8708249f6da47780`. Task 0 was captured at
`79c174860b12ce7b63804b36b717d6cb202a0922`; the three intervening commits add
or repair only
`docs/superpowers/plans/2026-08-03-nanopb-skip-string-production-promotion.md`.
`git diff --check` passed across that range.

The full evidence capture intentionally included one uncommitted, test-only
prerequisite in `tests/test_runtime_nanopb_private_read_pair.py`. It added the
reviewed Linux Clang profile to an existing production test without changing
firmware source, overlay configuration, manifests, package inputs, or official
blobs. That prerequisite is committed separately as
`34e2ddd3` (`test: reproduce nanopb private read pair on Linux`).

No signing, flashing, erase, reset, boot, display, radio, sensor, power, or G2
hardware operation was performed.

## Durable normalized evidence

The ignored raw logs remain supporting evidence. The clean-checkout authority is
the pair of closed version-2 normalized records:

| Profile | Durable record | Bytes | SHA-256 |
|---|---|---:|---|
| Apple Clang 21 | `nanopb-skip-string-regression-evidence-apple.json` | 28,591 | `5887ae8b53ed5bf5ac0d052e7b6c3dc51a75d1cef189b8bd7b5389ca23bb7f62` |
| Linux Clang 22.1.8 | `nanopb-skip-string-regression-evidence-linux.json` | 252,280 | `1cf027edcce1b8b52f2b328c88918db0b6ce1eff431cc92a8e2d3005a92aa905` |

Each record pins its raw log byte count, SHA-256, command status, complete
failure/error identities, complete delimiter-structured result-block hashes,
skip identities/reasons/line hashes, and resolution provenance. Aggregate counts
are not the regression authority.

The common source-backed resolver is
`nanopb-skip-string-skip-resolvers.json`: 866 bytes / SHA-256
`32bc885d9626d8589d87f89180f67ce2b798592c1bc3c38a6aff4697ef368795`.
It resolves the Apple run's sole anonymous skip line by authenticating the exact
source path, Git blob, class, `setUpClass`, reason literal, and source SHA at the
promotion base. The Linux capture has zero anonymous skip lines and therefore
normalizes identically with or without that resolver entry.

## Apple profile

Environment:

```text
OPENCFW_CLANG=/usr/bin/clang
OPENCFW_TOOLCHAIN_PROFILE=apple-clang
Apple clang version 21.0.0 (clang-2100.3.27.1)
```

The reviewed ten-module focused run executed 138 tests in 233.798 seconds and
passed with seven expected skips. Its complete raw output is 18,773 bytes /
SHA-256
`59ded0fc63ebf5fa3047bdc5784244349a64c94efbd6abd8f342c26702045d2c`.
The module set is:

1. `tests.test_runtime_nanopb_skip_string_candidate`
2. `tests.test_runtime_nanopb_decode_varint32_production`
3. `tests.test_runtime_nanopb_decode_varint_production`
4. `tests.test_runtime_nanopb_private_read_pair`
5. `tests.test_runtime_nanopb_read`
6. `tests.test_runtime_nanopb_skip_varint_production`
7. `tests.test_runtime_nanopb_decode_svarint_production`
8. `tests.test_nanopb_snapshot`
9. `tests.test_toolchain_profiles`
10. `tests.test_unittest_identity_baseline`

The authoritative full command was:

```text
python3 -m unittest discover -s tests -v
```

It recorded 2,660 tests in 1,771.587 seconds, 56 failures, zero errors,
13 skips, and expected command status 1. The raw log is 370,227 bytes /
SHA-256
`81459052c8c01c6157e6d3c09c4a5525b691abc16d40901b8c203b7c516e65d4`.

Relative to the preceding varint32 durable authority, Apple added zero failure
identities and zero error identities. Two historical failures disappeared:

- the now-source-owned missing varint32 candidate; and
- the repaired FreeRTOS scheduler-cluster rollback identity.

Normalized A/B generation, byte comparison, closed-schema reload, CLI
self-comparison, literal heading comparison, candidate-production exclusion,
and all accepted status sidecars passed. The independently reviewed Apple
evidence manifest contains 59 records and is 6,043 bytes / SHA-256
`33b76dcab6c490bbc23c84fc193b02a9f29637868869e8e176d419cedddab051`.

The pre-promotion Apple Build A/B inventories each contain 1,050 rows and match
the live production closure. No package, component, overlay, manifest, or
official-blob byte changed during Task 0.

## Linux profile

Environment:

```text
reviewed source root=/Users/kalani/Repo/SybilSightABCD/openCFW
OPENCFW_CLANG=/home/linuxbrew/.linuxbrew/bin/clang
OPENCFW_TOOLCHAIN_PROFILE=linux-clang
Homebrew clang version 22.1.8
```

The reviewed focused set was proven as an exact disjoint 7+3 union. The frozen
seven-module run and post-repair three-module complement both passed; the
complement ran 39 tests in 724.774 seconds with two expected skips. Candidate
production exclusion and frozen Build A/B reuse also passed.

The single authoritative full discovery recorded 2,608 tests in 9,136.580
seconds, 29 failures, 8 errors, 331 skips, and expected command status 1. Its raw
log is 559,872 bytes / SHA-256
`7631c71ee91d64846fb01a11c94f5a29c694d6687648251b4bcb451317323343`.

Literal comparison with the preceding Linux authority found:

```text
added failures: 0
removed failures: 0
added errors: 0
removed errors: 1
added skips: 0
removed skips: 0
```

The removed error is exactly
`setUpClass (test_runtime_nanopb_private_read_pair.NanopbPrivateReadPairProductionTests)`.
All 29 common failure blocks, all 8 common error blocks, and all 331 common skip
reason/line records are identical.

The hardened parser accepts the new raw log and intentionally rejects the prior
raw authority because that historical capture contains a buffered TLSF diagnostic
between the unittest summary and its appended `command_status`. The rejected
attempt is retained. The prior normalized record was regenerated twice from the
exact 558,794-byte historical raw hash using the parser pinned to commit
`419f84a8f8c7b8d496e292c06059a764c73d2dfc`, blob
`4433e0c05641d438c1b7d4ed544ad36d123c579d`, then loaded and compared by the
current closed-schema code. The new raw log was parsed only by the hardened
current parser. Prior and current normalized A/B comparisons and CLI comparisons
all passed.

The independently validated Linux evidence root is
`/tmp/opencfw-skip-string-task0/post-repair-linux`. Its comprehensive manifest
contains 77 records and 5,924,505 payload bytes; the 8,260-byte manifest SHA-256
is
`76b8a87ed0cd4ffb1adc3c01c81df79beaeb4e59d2d5350772555e2b02f4f0f1`.
The validator recomputed every payload hash, 23 accepted status sidecars, the
5,364-file host/container tracked mirrors, seven provider pins, focused union,
candidate exclusion, frozen 60-record build index, and final worktree integrity.
Fifteen explicitly prefixed `rejected-*` diagnostics are listed in the manifest
and consumed by no accepted proof.

## Acceptance rule for the promotion

For each reviewed profile, compare future full discovery against its own durable
record. The promotion must add no failure or error identity. Counts alone are
insufficient, and Apple/Linux identities must not be merged because their
toolchain-specific skip and error sets intentionally differ.

The current parser also requires `command_status` to be the final record and
rejects any non-whitespace text between the unittest summary and that status.
This prevents buffered post-summary diagnostics from silently entering a durable
baseline.
