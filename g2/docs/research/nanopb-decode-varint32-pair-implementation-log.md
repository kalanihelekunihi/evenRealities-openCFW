# Nanopb decode-varint32 pair: Task 8 implementation log

Date: 2026-08-03

Reviewed range:
`4abb9c10935c244e365fd4d3ebc911a960a20e5b..29cc1b284b4f8604b00fac7cb7fd112b93b9d95e`

Original whole-tranche reviewers:

- Spec/evidence: `/root/varint32_task7_spec_reviewer`
- Quality: `/root/varint32_task7_quality_reviewer`

Additional repair checks:

- Read-only repair review: `/root/varint32_task8_repair_reviewer`
- Read-only baseline audit: `/root/varint32_task8_baseline_auditor`

## Findings and dispositions

### Historical anonymous-skip provenance

Severity: Important. Original disposition: NOT APPROVED.

Both original reviewers found that the Task 0 resolver authenticated the
historical signed-varint test SHA-256
`e7d21035166e3d7b10a9b767f007331c08e1b64b22e2c1d214da4b06e889adf8`
against the mutable HEAD file, whose SHA-256 had become
`247e6c8e5493e4851675407b0d7bfec4bc0f0b8fac8b2b09967d99327dbfaf8b`.
This made three of the 14 identity tests raise `MalformedEvidence`.

Disposition: fixed without repinning historical truth. The resolver and normalized
evidence are explicitly closed version 2. They pin Task 0 commit
`4abb9c10935c244e365fd4d3ebc911a960a20e5b`, path
`openCFW/tests/test_runtime_nanopb_decode_svarint_production.py`, Git blob
`6b93a951c6c0be881a7758b8da729163f765bf52`, and the original SHA-256. The
loader resolves commit to tree path to blob with argv-only Git calls, parses and
validates the historical Python bytes, and never falls back to the mutable HEAD
file. Missing or malformed revisions, non-commit revisions, unavailable history,
changed path/blob bindings, changed blob pins, unsafe paths, changed content hashes,
and non-Git roots fail closed.

Original RED:

```text
python3 -m unittest -v openCFW.tests.test_unittest_identity_baseline
Ran 14 tests: FAILED (errors=3)
All three errors: resolutions[0].provenance source SHA-256 differs
```

The new revision-aware executable contract was also replayed temporally against
the pre-repair implementation. Its six focused tests used guard-specific error
expectations, so the old loader's generic unsupported-v2 error could not satisfy
the negative gates:

```text
python3 -m unittest -v openCFW.tests.test_unittest_identity_historical_contract_red
Ran 6 tests: FAILED (failures=5, errors=1)
```

With the implementation reapplied, the exact same six identities passed. Those
cases were then retained in `tests/test_unittest_identity_baseline.py`; the
temporary replay-only module was deleted.

### Complete non-linking branch set

Severity: Important. Original disposition: NOT APPROVED.

The quality reviewer found that the exact complete `B.W` expected set in
`tests/test_core_overlay.py` omitted the two new production patch sites even though
the component report contained them.

Disposition: fixed by adding exactly
`replace_nanopb_decode_varint32_eof` and
`replace_nanopb_decode_varint32`. The gate retains exact set equality and still
decodes every branch target and checks the complete two-byte NOP tail.

Original RED:

```text
python3 -m unittest -v \
  openCFW.tests.test_core_overlay.ApolloCoreOverlayTests.test_entry_replacements_are_nonlinking_branches_with_nop_fill
Ran 1 test: FAILED (failures=1)
Extra actual sites: replace_nanopb_decode_varint32_eof,
replace_nanopb_decode_varint32
```

### Version-2 test-control vacuity found during repair

Severity: Important. WIP disposition from the read-only repair reviewer: fix
required before approval.

After the schemas moved to version 2, the synthetic normalized-evidence `good`
fixture still declared version 1. Its negative mutations therefore all failed at
the version check instead of exercising their intended schema, count, and status
contradictions.

Disposition: fixed. The unmutated version-2 fixture is loaded first as a positive
control. Independent version-1, version-3, unknown-format, extra-key, count, and
command-status mutations then each fail closed.

### Skip reason was not bound to the selected class hook

Severity: Important. Same-reviewer follow-up disposition after commit `6b924d31`:
NOT APPROVED until fixed.

The resolver required the selected class to contain a `setUpClass`, but searched
for the skip reason anywhere in the authenticated source file. Changing
`source_class` to `NanopbDecodeSvarintProductionTests` and updating the resolved
identity was therefore accepted even though the reason belongs only to
`NanopbDecodeSvarintLinuxBuildMutationTests.setUpClass`.

Strict RED:

```text
python3 -m unittest -v \
  openCFW.tests.test_unittest_identity_baseline.NormalizedEvidenceTests.test_resolver_rejects_reason_bound_to_different_class
Ran 1 test: FAILED (failures=1)
MalformedEvidence not raised
```

Disposition: fixed. The authenticated module must have one direct, unaliased,
unshadowed `import unittest`; the uniquely selected top-level class must have one
direct synchronous `@classmethod setUpClass(cls)` with the exact callable
signature; and its non-nested method body must have exactly one
`raise unittest.SkipTest(<exact reason string literal>)` with one positional
argument and no keywords. Constructor-only calls, unproven aliases, wrong
exceptions, extra arguments, duplicate raises or hooks, async hooks, other
methods/classes, nested scopes, and module/class/method shadowing fail closed.
The original wrong-class identity and the targeted AST mutation matrix are GREEN.
An Important WIP compatibility regression that directly referenced newer
`ast.MatchAs`/`ast.MatchStar` classes produced 33 errors on the supported Python
runtime; feature-detected match-binding nodes now preserve the same fail-closed
check when available without breaking older runtimes.
Same-reviewer re-review of the follow-up commit is complete with no findings.

## Verification status

The repair implementation and focused RED-to-GREEN replay are complete:

- Historical replay contract: 6/6 GREEN after the pre-repair 5F/1E RED.
- Durable identity module: 15/15 GREEN for the first repair and 17/17 GREEN
  after the same-reviewer AST-binding follow-up.
- Five core/package quality invariants: 5/5 GREEN, including the exact complete
  `B.W` set/target/NOP-tail gate.
- Nanopb snapshot module: 20/20 GREEN.
- Toolchain-profile module: 33 tests, 29 GREEN and 4 expected skips because the
  available compiler is not a recorded alternate profile.
- The real Task 0 CLI evidence comparison exited zero from both the repository root
  and `/tmp` with absolute paths.

The version-2 normalized evidence is 28,762 bytes, SHA-256
`1300c8544b5ef5d7bb775ec5b25f93367f5312a10793dfaba1471855e0d0f417`.
The version-2 resolver is 866 bytes, SHA-256
`7b4a2c774d61096e74048111d77f81db385afb4b395cfff3f10c6e3fad95108b`.

This repair changes tests, the identity-evidence tool, and research records only.
It leaves the Apple/Linux firmware sources, manifests, and toolchain profiles
unchanged. The canonical firmware pins remain those in
`nanopb-decode-varint32-pair-source-audit.md`: overlay
`a21779625714a5c029652287e38939ac4290306b3a8781045501839d385a1c62`,
component
`99b1718f989695a4fe39655e8cf31ea7ef19ce97ed96b70fc1796c847bd2dead`,
package
`92d1d9a2f2d80b503b2b68d1533a1c990da5a215381a0a22b604e63b6f7fb229`,
build report
`eb0c87492532f136569cb529b2202805bd8bd84a45f76e0538b4ec1822bfe1b7`,
and flash plan
`1ee4d8d5a21a2b0d79173c5b78bcdf752407ae0e26d086ea5c5df4b504c939d9`.

## Final same-reviewer verdicts

The original reviewers re-inspected the full range
`4abb9c10935c244e365fd4d3ebc911a960a20e5b..ca17588400e1ea82f676c434c4d28e6f24695860`.

- Spec/evidence reviewer `/root/varint32_task7_spec_reviewer`: **COMPLIANT** at
  `ca17588400e1ea82f676c434c4d28e6f24695860`, with no findings. The review
  confirmed 17/17 identity tests, Python 3.9 compatibility, non-vacuous temporal
  RED-to-GREEN and AST mutation evidence, and the exact four-path follow-up scope.
- Quality reviewer `/root/varint32_task7_quality_reviewer`: **APPROVED** at
  `ca17588400e1ea82f676c434c4d28e6f24695860`, with no findings. The review
  confirmed 17/17 identity tests; the 58-test quality matrix with four expected
  compiler-profile skips; Task 0 CLI comparison status zero from both the
  repository root and `/tmp`; a detached clean-checkout run with 16 passes and one
  expected ignored-supporting-log skip; and the exact four-path AST delta.

The final authenticated logs are:

- Identity: SHA-256
  `254dffc7690c87845753cd2ae413e7b4a6343d06f30155f04b88c510e0c8755c`.
- Quality: SHA-256
  `1c75a60b8589a1a7b02dc60f9119a3eb8ab7124398fd528aef6127ca96fa2710`.
- Cwd-independent CLI: SHA-256
  `7eb4e0c76d9dcb48536c02362d76f46fe3696328ef7ec6a0ae013e644a5b5982`.

All Critical/Important review findings are closed. The Task 8 independent review
gate is satisfied.

Hardware boot, flashing, signing, reset, and on-device testing remain explicitly
outside this task.

# Nanopb decode-varint32 pair: Task 9 final-gate log

Date: 2026-08-03

Reviewed repair range:
`112950f303dcc598dc444803a5c3a90dcd9b12ba..419f84a8f8c7b8d496e292c06059a764c73d2dfc`

Task 9 Linux regression authority:
`b6260d5f4c24ccb9fd2a1334780a01880ff19c42`

Final-gate implementer:
`/root/varint32_task9_final_gate_implementer`

Independent Linux auditor:
`/root/varint32_task9_linux_auditor`

## Final-gate repairs

### Profile-aware focused gates

Commit `f28449f9a6cd75595a3b050949e4935503f20429`
(`test: make nanopb focused gates profile aware`) closes two Apple-only test
assumptions found by the independent audit:

- The skip-string candidate had hard-coded the Apple compiler object, text, and
  relocation identity.
- The varint32 production test had hard-coded the Apple public-varint predecessor
  patch address and bytes.

The corrected tests resolve one of two reviewed profiles and require the exact
reviewed compiler path and version. Unknown profiles, incorrect paths, near-version
matches, and other unreviewed compiler identities fail closed. The public-varint
predecessor patch is now selected from the active profile and bound to the build
report:

- Apple target `0x007b2c40`, bytes `23f347bb00bf00bf00bf`.
- Linux target `0x007b3360`, bytes `23f3d7be00bf00bf00bf`.

### Final Linux profile consumers

Commit `419f84a8f8c7b8d496e292c06059a764c73d2dfc`
(`test: repair final Linux profile consumers`) closes three new identities exposed
by the complete post-`f28449f9` Linux diagnostic discovery:

1. The LittleFS rewind gate retained the stale plan total `853`; the active Linux
   plan contains `854` entries. The gate now derives and checks the total against
   the plan categories.
2. The scheduler accounting pins omitted the 252-byte varint32 source tail and the
   256-byte replacement span. The Linux accounting now binds the source increase,
   both generated/replaced span increases, and the corresponding opaque decrease.
3. The EasyLogger host fixture used generic `cc`, which selected GCC rather than
   the reviewed clang and failed under `-Werror=sign-compare`. The fixture now
   uses the same reviewed clang as the production overlay.

The rollback audit also found that the active Linux legacy prefix was exact except
for the omitted six-byte in-place `open_cfw_littlefs_tag_chunk` restoration at
component offsets `[601792, 601798)`. Restoring that patch recreates the prior
Linux component identity exactly. The shared rollback reconstruction now restores
that site; the post-repair conditional Apple rollback remains exact.

The two repair commits change five test/profile-consumer files only. They do not
change production firmware sources, linker placement, manifests, or generated
firmware bytes.

## Apple final evidence

The authoritative full Apple discovery ran at
`419f84a8f8c7b8d496e292c06059a764c73d2dfc` with reviewed compiler
`/usr/bin/clang` and profile `apple-clang`. The focused repair exercises below
also used that compiler/profile: the 85-test tranche ran after `f28449f9`, while
the eight-test consumer and conditional rollback runs exercised the relevant
working-tree repairs subsequently committed as `419f84a8`.

The corrected focused tranche was GREEN: 85 tests, four expected alternate-profile
skips, 223.257 seconds, status zero. Its 11,346-byte log has SHA-256
`8f7470fdc2093fb5ad048f060440f6ce8ffcbc9bf39ceec760ffe511d829889c`.

The eight affected profile-consumer tests were GREEN in 79.196 seconds, status
zero. Their 1,364-byte log has SHA-256
`f8ce66b47c2e33f2b9d06474b149caa237afeb7dc7b3b5eb213e5347fe1a1088`.
The final conditional Apple rollback identity was independently GREEN in 30.185
seconds, status zero. Its 268-byte log has SHA-256
`36f745e2adb105c41e841f9bc1e9e15cdaeb570f4a225b2cf79f20ff80e2f4c7`.

The post-commit full discovery produced:

```text
Ran 2658 tests in 1983.372s
FAILED (failures=56, skipped=13)
command_status=1
```

This is the expected historical-failure outcome, not the regression decision.
The full 369,963-byte log has SHA-256
`4445643ae0ea9717f2d9e79da7303673c94cd18f353e7adbddc76b97c00eecb9`.
The existing version-2 resolver/evidence CLI exited zero for the structured
unittest failure, error, and skip identities. Both the post-`f28449f9` authority
and post-`419f84a8` capture contain the same C-stdout line,
`tlsf_create: Memory must be aligned to 8 bytes.`, between the unittest summary
and appended command-status record. The current parser does not reject or model
text in that interval, so zero status does not independently authenticate that
suffix structurally. The complete-log SHA-256 pins all captured bytes, and an
independent exact heading-set comparison found no new or resolved failure/error
identities. Apple acceptance remains bounded to those facts; Task 0 must reject
unmodeled post-summary text and capture C stdout line-buffered, or explicitly
model and authenticate it.

Exact structured comparison against the post-`f28449f9` Apple authority produced:

```text
baseline_tests=2658
baseline_failures=56
baseline_errors=0
current_tests=2658
current_failures=56
current_errors=0
current_skips=13
current_command_status=1
failure_headings_unique=True
error_headings_unique=True
NEW_FAIL=[]
NEW_ERROR=[]
RESOLVED_FAIL=[]
RESOLVED_ERROR=[]
```

The 273-byte comparison log has SHA-256
`b2846a0cd91760b1a62421f54e48664f85443a8d3a7e5ae8ca6255ee425e2135`.
The current documentation-only diff passes `git diff --check`; no separately
retained Apple clean-state record is claimed here.

Task 9 does not alter the previously authenticated Apple source-build outputs.
Two source builds remained byte-identical across 1,043 generated files. Their
relative-manifest SHA-256 was
`888ec5177c9a0841935e8404f01b99ac18b8e261d3baa4f6cd21a7f0589683c3`,
and the two source logs had SHA-256
`fb707c0eec1cc13aa4c3c982da47c85b1093221c3b5129f380cfc660a3f6b91f`.
The canonical Apple artifacts remain:

- Overlay, 125,222 bytes:
  `a21779625714a5c029652287e38939ac4290306b3a8781045501839d385a1c62`.
- Component, 3,648,618 bytes:
  `99b1718f989695a4fe39655e8cf31ea7ef19ce97ed96b70fc1796c847bd2dead`.
- Package, 4,427,112 bytes:
  `92d1d9a2f2d80b503b2b68d1533a1c990da5a215381a0a22b604e63b6f7fb229`.
- Build report:
  `eb0c87492532f136569cb529b2202805bd8bd84a45f76e0538b4ec1822bfe1b7`.
- Flash plan:
  `1ee4d8d5a21a2b0d79173c5b78bcdf752407ae0e26d086ea5c5df4b504c939d9`.

## Linux baseline and intermediate RED evidence

The exact Linux root is `/Users/kalani/Repo/SybilSightABCD/openCFW`. The reviewed
compiler is `/home/linuxbrew/.linuxbrew/bin/clang`, exact version
`Homebrew clang version 22.1.8`, with profile `linux-clang`. Git environment
overrides were unset and `PYTHONHASHSEED=0` was used for final regeneration and
gates.

The Task 9 `b6260d5f` baseline authority is 551,736 bytes with SHA-256
`0bcbef355c103ca13ec5e7df89bd1cc4ee6adb3680f5ebc7430dfc18e13435a4`.
It records 2,549 tests, 31 failures, 10 errors, and 330 skips.

The complete post-`f28449f9` Linux discovery was retained as RED diagnostic
evidence. It ran
2,593 tests in 9,637.602 seconds with 32 failures, 10 errors, and 331 skips. Its
561,666-byte log has SHA-256
`22ea4bab4d3ba7965987e4eee6d28e7a631efb56adbf112d8f816fc9deee27c4`.
Exact heading-set inspection identified the three profile-consumer defects
described above; it also showed the old missing-varint32-candidate failure
resolved.

## Invalid Linux provider-loss diagnostic

The first attempted post-commit Linux discovery was not a valid regression run.
The exact-root copy lacked an ignored generated provider,
`components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin`. A separate
class reproduction failed in `setUpClass` before running any tests when
`open_cfw.py` attempted to read that provider:

```text
Ran 0 tests in 133.508s
FAILED (errors=1)
command_status=1
```

The isolated 2,473-byte diagnostic log has SHA-256
`a75baed724dedc713dd30413858a38b52435ec24c39808198b4cc4f91027fe06`.
This is environmental provider-loss evidence, not a Task 9 result identity.

The invalid partial full discovery was deliberately terminated and preserved
separately with status 143. It contains 1,657 lines and 345,927 bytes, SHA-256
`cded9411755fb9fb79aea806f7a6f02bd493ac53d3794d40187eff008fb3636a`.
It is explicitly non-authoritative and must not be used for baseline comparison,
test counts, or acceptance.

## Linux source regeneration and focused preflight

The ignored generated providers were restored only by the normal source-build
workflow, `./make.sh source`, at final commit `419f84a8`. The command completed
with status zero. Its 51-line, 3,529-byte log has
SHA-256
`85f555910bd9e423e0bfab98b34ba396dbc24469e65706ba7a56bfeb808a2a10`.
All vendor snapshot checks, including the nanopb 0.4.9 compatibility snapshot,
were GREEN. The path-scoped tracked `openCFW/` status remained clean after
generation.

Regenerated Linux identities are:

- Core overlay, 127,046 bytes:
  `593833cbe89b7f195f97d0e9bef8b57c98c4efe4b7cf13a035b4604738c38364`.
- Core component, 3,650,442 bytes:
  `2712b0ca1feef4e75cb25c0d619814273d06d4aa82fbe85feb29dd874107c5ef`.
- Source package, 4,428,936 bytes:
  `2a3c7b0298f3dcd52dc05fc3b0cbcf0bd3e282daa9c3b93ba47e4deff442865b`.
- Bootloader overlay, 662 bytes:
  `e4c743531f56c190b7e3129768d410480a2f3433a5b680c7bf432ef0b05a7021`.
- Bootloader component, 149,262 bytes:
  `fc3d07c8a59e1c33f26965cdb1888114412c3ca671d6137f7c3166acc81c8d74`.
- Ring text, 160 bytes:
  `0535cf0a9a3ffc2729f3e7d6182d7cdff7fedd81df418f95a1b228cfa3d13edc`.
- Ring component, 3,523,556 bytes:
  `fabeb5cedc0f82ad248c1ff96cd90944ec1cde7d827ecb3010f6ea7db9ca93dc`.

After regeneration, the previously blocked FreeRTOS+CLI class entered its test
methods successfully. It ran seven tests in 138.586 seconds: six passed and one
known baseline identity failed because that older focused test retains a stale
pre-varint32 package pin. Status was one. The 36-line, 2,864-byte focused log has
SHA-256
`0fb3ad859d6b5747d9eaf350e5982c2fc365474a0dfdaa86f0581679c86455a8`.
This preflight proves that provider restoration fixed the `setUpClass` error; its
known package-pin failure remains subject to the full identity comparator rather
than being treated as a new setup error.

## Linux final full discovery

The valid post-regeneration discovery completed at `419f84a8`:

```text
Ran 2599 tests in 10062.958s
FAILED (failures=29, errors=9, skipped=331)
command_status=1
```

The 3,312-line, 558,794-byte log has SHA-256
`22bdb156e5175bb0e88e7b3bf9a023e7101ea9fa50a45a74a72e27c14ab74d4b`.
The command-status sidecar contains `1`, matching the expected nonzero historical
failure outcome. The project parser accepted the structured result identities as
2,599 tests, 29 failures, nine errors, 331 skips, and command status one. All 38
failure/error headings are unique.

The final log contains the same buffered C-stdout diagnostic as the Apple and
post-`f28449f9` authorities,
`tlsf_create: Memory must be aligned to 8 bytes.`, between the unittest summary
and appended command-status record. As disclosed above, the current parser does
not structurally authenticate that interval. The complete-log SHA pins the line,
and the comparison below authenticates every structured result block and body.
Task 0 must close this capture/parser gap before establishing the next regression
authority.

Exact comparison against the complete post-`f28449f9` Linux diagnostic authority
found no new failure or error identity:

```text
baseline_tests=2593
baseline_failures=32
baseline_errors=10
baseline_skips=331
current_tests=2599
current_failures=29
current_errors=9
current_skips=331
current_command_status=1
failure_headings_unique=True
error_headings_unique=True
NEW_FAIL=[]
NEW_ERROR=[]
RESOLVED_FAIL=[
  test_active_profile_package_plan_and_ownership_are_exact
    (test_runtime_littlefs_file_rewind_private.RuntimeLittlefsFileRewindPrivateProductionTests),
  test_component_accounting_equations_and_profile_pins_are_exact
    (test_runtime_freertos_scheduler_cluster.RuntimeFreeRTOSSchedulerClusterTests),
  test_exact_stock_and_tail_rollback_recreates_prior_component
    (test_runtime_freertos_scheduler_cluster.RuntimeFreeRTOSSchedulerClusterTests),
]
RESOLVED_ERROR=[
  setUpClass
    (test_runtime_easylogger_hexdump_production.RuntimeEasyLoggerHexdumpProductionTests),
]
```

The six-test increase is the expected effect of resolving the EasyLogger
`setUpClass` error: those six class methods now execute and pass. Every one of the
29 failure blocks and nine error blocks shared with the `f28449f9` authority has
an identical project-parser block SHA-256 and body SHA-256. In particular, the
historical LittleFS tag-type3 setup error remains byte-identical: block SHA-256
`eaef20f43d5c75bd9f39cd022359b21d79864dcf33375767efc6fff6edb0cbdc`,
body SHA-256
`cd1e0692a62e17c3da7eee72a310b80f2e518dc7cbd799643499064ecaecc1f3`.

Comparison to immediate Task 9 baseline `b6260d5f` also produced no new failure
or error heading. It resolved the missing varint32 candidate-source failure, the
skip-string candidate `setUpClass` error, and the scheduler rollback failure.
The older `b6260d5f` raw capture is not accepted by the current parser because its
buffered TLSF line follows the summary without a final command-status record; its
complete log and exact heading sets remain separately hash-pinned baseline
evidence.

The exact-root copy is not itself a Git checkout. The final proof evaluates it as
an explicit work tree against the active `g2-2.2.7-cfw` Git directory and records:

- HEAD `419f84a8f8c7b8d496e292c06059a764c73d2dfc`.
- 2,221 tracked `openCFW/` files.
- Empty path-scoped tracked status.
- `git diff --quiet HEAD -- openCFW` status zero.
- `git diff --check` status zero.
- Tracked `openCFW/` tree OID
  `45df01973ded8fa4ffa5da60a5ede5a1aae904ce`.

Generated providers remained present throughout the valid run, and the canonical
core, bootloader, and ring artifact identities remained those recorded in the
source-regeneration section.

## Independent final review

The independent Linux auditor returned **GO** after reviewing the entire final
implementation-log diff at `419f84a8`. The audit directly verified the five-file,
two-commit repair scope; all final Linux counts, hashes, exact identity sets, and
common block/body digests; all seven preserved generated artifact identities; the
TLSF/parser limitation; both baseline comparisons; and the exact-root work-tree
proof. The auditor's one finding corrected an overstatement about the shared
LittleFS rollback restoration. After that correction, `git diff --check` passed
and no remaining evidence, scope, or hardware-caveat discrepancy was found.

The authenticated 4,113-byte, 74-line review log is
`/tmp/opencfw-task9-linux-compare-host/final-419f84a8-comparison-review.txt`,
SHA-256
`813f87b6ad51b1c9984ec17a5b6217ff8dd412742048162b6cd39025c40326cf`.

## Scope and deferred hardware caveats

- The nanopb source is authenticated as a 0.4.9-compatible baseline. This does
  not unequivocally identify the vendor firmware's exact nanopb point release or
  every vendor configuration parameter.
- Expected historical failures remain in the full discovery suites. Acceptance
  is based on complete structured result identities and no new failure/error
  identities, not a zero-failure summary.
- Binary blobs and opaque regions outside this bounded decode-varint32 pair remain
  in place and require separate source-replacement work.
- Hardware signing, flashing, reset, boot, display, BLE/radio, sensor, battery,
  sleep, and power testing are explicitly deferred. No claim of on-device
  execution, bootability, radio correctness, or flash safety is made by Task 9.
- No signing keys, flash operations, device resets, or hardware state changes were
  used during this gate.

Apple final gate: **CLOSED — no new failure or error identities.**

Linux final gate: **CLOSED — no new failure or error identities.**

Task 9 overall: **CLOSED — APPLE AND LINUX FINAL EVIDENCE APPROVED.**
