# Nanopb `pb_skip_string` Production Promotion Plan

> Status: bounded implementation plan. This document authorizes source, test,
> offline target-build, manifest, provenance, and documentation changes only. It
> does not authorize signing, flashing, resetting, booting, or otherwise operating
> G2 hardware.

## Goal and non-negotiable boundary

Replace the complete stock `pb_skip_string()` body at
`[0x0048F64C,0x0048F66C)` with one Zlib-licensed source leaf and one full-span
non-linking entry redirect. The source leaf must decode the length by calling the
already source-owned public `open_cfw_nanopb_decode_varint32` provider and must
discard the payload by calling the already source-owned
`open_cfw_nanopb_read` provider. Both calls must be strict `target_function`
relocations. Fixed-address calls back to `0x0048F5AE` or `0x0048F3BE`, retained
stock instructions inside the 32-byte span, or promotion of the surrounding
`pb_skip_field()` dispatcher are outside the accepted implementation.

This is a source-ownership and offline reproducibility promotion, not proof of
Even Realities' historical nanopb checkout. The selected authority is the
authenticated nanopb 0.4.9 snapshot. The pristine `pb_skip_string()` definition
is byte-identical in authenticated nanopb 0.4.7, 0.4.8, and 0.4.9; controlled
target builds therefore cannot identify one exact vendor point release or exclude
a vendor backport.

The preceding varint32 tranche's final Linux full-discovery run is still pending
at plan-authoring time. This plan does **not** claim that gate is complete. Task 0
must begin only after that tranche records its final clean reviewed commit and its
Apple/Linux regression evidence. The resulting commit, rather than this plan's
authoring commit, becomes `PROMOTION_BASE`.

Every implementation task follows strict RED -> GREEN discipline: add or transform
the smallest executable contract first, run it and preserve the intended failure,
make only the scoped implementation change, and rerun focused and adjacent gates. A
test first run after its implementation is not RED evidence and must be reverted and
replayed in the correct order.

### Commit and gate policy

RED evidence and committed state are different things. A focused phase command may
fail while proving that a new contract detects the missing implementation. The only
committed RED authorized by this plan is the bounded Task 1 test/fixture commit. It
must change no production source, overlay, manifest, provenance, or current aggregate
pin, and its exact allowed failure set is specified in Task 1. Tasks 2-4 are
uncommitted working-tree checkpoints layered on that contract. Task 5 closes source,
overlay, real-builder, ownership, provenance, and current-documentation changes in
one atomic GREEN production commit. Tasks 6 onward also commit only while GREEN.

The **focused phase gate** is the named skip-string production module plus the
adjacent real-provider modules. Its exact Task 1 RED is allowlisted temporarily.
The **active aggregate/current-consumer gates** are `./make.sh source`,
`./make.sh verify`, `make vendor-snapshots`, nanopb snapshot verification,
core-overlay/package/manifest and toolchain-profile modules, full discovery, and the
Task 0 identity comparison. They are never allowlisted as a production regression.
They may expose expected stale pins while Tasks 2-4 exist only as uncommitted work,
but no intermediate production commit or promotion claim may be made. Before the
Task 5 atomic promotion commit, every focused identity and every active aggregate
gate must be GREEN, except only the pre-existing Task 0 full-discovery identities.
Those pre-existing identities must compare exactly with zero new failure/error
identities. The same condition is mandatory before Linux recording, independent
review, and the final report.

Every allowlisted identity below is the literal unittest result-heading identity
captured after `FAIL: ` or `ERROR: ` by
`tools/unittest_identity_baseline.py`; no dotted-name normalization is permitted.
The required spelling is `test_method (test_module.Class)`.

## Pinned evidence and implementation invariants

### Official image, stock span, and adjacent owners

The official Apollo-main OTA package is 3,523,396 bytes / SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
Its 32-byte preamble is excluded from the installed application, whose runtime
base is `0x00438000`; equivalently, runtime address equals OTA component file
offset plus `0x00437FE0`.

The stock function starts at installed-application offset 357,964 and OTA
component file offset 357,996:

| Owner | Runtime span | Bytes | SHA-256 |
|---|---:|---:|---|
| predecessor `pb_skip_varint` | `[0x0048F628,0x0048F64C)` | 36 | `fae83b1a62a07bb9c7a3d3f6c398bc13433ebe1cd75d01945f83f30e6fcc9c5d` |
| promoted `pb_skip_string` | `[0x0048F64C,0x0048F66C)` | 32 | `03afe2d60436676fffba342c7b8c9504992fa903d7cba768396fd1de2c6c66cd` |
| successor bytes before dispatcher | `[0x0048F66C,0x0048F6A0)` | 52 | `727a94d16ba7b4018c3addee83a6c63e87f0c3f2a3fe6afdb315549d10f53114` |

The exact 32-byte body is:

```text
1cb5040069462000fff7abff002801d1002004e0009a00212000fff7aafe16bd
```

The production patch must authenticate all 32 stock bytes before writing one
four-byte Thumb `B.W` followed by exactly fourteen `00bf` NOP halfwords. It must
also preserve and re-authenticate both adjacent owners above.

The current canonical manifest owns a 382-byte official region starting at file
offset 357,996 / runtime `0x0048F64C`. Promotion must split that region exactly
into:

- a 32-byte generated source-entry replacement at file offset 357,996 /
  runtime `0x0048F64C`; and
- a 350-byte official region at file offset 358,028 / runtime `0x0048F66C`.

No official subregion may remain inside the replaced 32 bytes, and the 350-byte
remainder must be byte-identical to the predecessor manifest's official slice.

### Caller, ingress, and outgoing dependency closure

The sole direct caller is the `PB_WT_STRING` arm of stock `pb_skip_field()`:

| Evidence | Pin |
|---|---|
| call | `BL 0x0048F6C6 -> 0x0048F64C` |
| encoding | `fff7c1ff` |
| encoding SHA-256 | `d853ba90900fc8e2d53ad28a1f280f1d57ea929840940aadf24677f15084deb2` |
| little-endian caller-address SHA-256 | `1244ca9de72fad315ed29b1fe0c617f93911a8f612d18cde18eaaa24f881c062` |
| address-plus-encoding SHA-256 | `0f659a755ea72cc876baf1bae460c9c07790f52d2e579c1fa5bdfa6fb442f6d6` |
| complete caller span | `[0x0048F6A0,0x0048F6EA)`, 74 bytes |
| caller-span SHA-256 | `36089daffbbc82abad65d97ae0fd64b58b8ad227ed585aa704611bc30369912d` |

Whole-application halfword-aligned `BL`, `B.W`, wide-conditional, narrow branch,
and `CBZ`/`CBNZ` scans plus byte-granular stored-pointer scans found no other entry
or interior ingress. The unchanged caller must continue to enter the stock address,
which becomes the complete `B.W` redirect; it must never be rewritten to the
profile-dependent relocated address.

The stock body has exactly two outgoing calls:

| Call site | Encoding | Stock target | Required source provider |
|---|---|---|---|
| `0x0048F654` | `fff7abff` | public `pb_decode_varint32` at `0x0048F5AE` | `open_cfw_nanopb_decode_varint32` |
| `0x0048F666` | `fff7aafe` | `pb_read` at `0x0048F3BE` | `open_cfw_nanopb_read` |

The new leaf must therefore contain exactly two `R_ARM_THM_CALL` relocations,
at text offsets `+0x08` and `+0x14`, with symbol and `target_function` spelling
identical to the two source providers. Neither relocation may use
`target_address`. No third undefined runtime symbol, local data closure, writable
section, or fixed hardware address is allowed.

### Authenticated upstream and ABI boundary

Use tag `nanopb-0.4.9`, commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`, tree
`2c4c260bcff3f9f7081238d377274dd385d76582`, the vendored 53,845-byte
`pb_decode.c` / SHA-256
`e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a`,
and the unchanged upstream Zlib license.

Definition hashes use exact source bytes from the first byte of the function
signature through its matching closing brace, with no following delimiter bytes or
normalization. The pristine definition is 299 bytes / SHA-256
`8da14b4cc741fc15884b11d3447d0c2c529f65c31b3823170837229d36f81585`
in all three authenticated releases:

| Release | Commit | `pb_decode.c` span |
|---|---|---:|
| nanopb 0.4.7 | `b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba` | `[8276,8575)` |
| nanopb 0.4.8 | `6cfe48d6f1593f8fa5c0f90437f5e6522587745e` | `[8276,8575)` |
| nanopb 0.4.9 | `98bf4db69897b53434f3d0ba72e0a3ab1a902824` | `[8362,8661)` |

The recovered target ABI has 32-bit `size_t` and 32-bit `uint32_t`. Upstream's
`(size_t)length != length` check is consequently tautologically false on the target
and emitted no stock branch or `"size too large"` data dependency. The altered
production source must preserve static assertions for that ABI and implement the
emitted two-call path:

```c
if (!open_cfw_nanopb_decode_varint32(stream, &length)) {
    return false;
}
return open_cfw_nanopb_read(stream, NULL, (size_t)length);
```

This target-specific adaptation must remain conspicuously marked as altered source.
It must use the existing recovered stream ABI rather than introducing a duplicate
structure definition.

The authenticated 148,599-byte bootloader / SHA-256
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`
contains neither the exact stock body nor the selected 8- and 12-byte boundary
probes. Scope is Apollo-main only. This is a bounded exact-body exclusion, not proof
that no differently compiled nanopb behavior exists in the bootloader.

### Qualified candidate and projected production placement

The existing production-excluded candidate is already qualified by
[`nanopb-skip-string-source-audit.md`](../../research/nanopb-skip-string-source-audit.md).
Apple Clang 21.0.0 and exact-root Homebrew Clang 22.1.8 both produced the same
1,044-byte candidate object / SHA-256
`f059f1c161bb602413d0505e51f6253283bf589622159c0fe4ee4202153e2b72`
and the same 34-byte, four-byte-aligned unrelocated text / SHA-256
`d3216f569354900680dae5d78350af7668be4d8fbdae64a47afc4f440b0df920`.
The object exposes only the two call seams above, allocates no writable data, and
has the normal eight-byte CANTUNWIND association. Production naming changes the
ELF string table and source pins, so the production object must be re-observed and
must not inherit the candidate's whole-object hash by assumption.

The completed varint32 source audit currently pins these predecessor ends:

| Profile | Current overlay end | Projected alignment | Projected skip-string leaf | Projected new end |
|---|---:|---:|---:|---:|
| Apple Clang 21.0.0 | offset 125,222 / `0x007B2C4A` | 2 bytes | offset 125,224 / `0x007B2C4C`, 34 bytes | 125,258 / `0x007B2C6E` |
| exact-root Linux Clang 22.1.8 | offset 127,046 / `0x007B336A` | 2 bytes | offset 127,048 / `0x007B336C`, 34 bytes | 127,082 / `0x007B338E` |

With those exact predecessor offsets and direct source-provider calls, the projected
relocated text is identical in both profiles, SHA-256
`3b1a0dbe465d562770e02d5afe04357087a6bfee22342a0f6844986a0161f547`.
The projected Apple replacement is `23f3feba` plus fourteen `00bf` halfwords,
SHA-256
`86ba480676461c25f262f93c3d1cc0e0e6080e6c44c367a261e1ac857ce81c3d`;
the projected Linux replacement is `23f38ebe` plus fourteen `00bf` halfwords,
SHA-256
`738d3ad448d28a408c0aaa76f7c7188181966ac44bc22afe675bde4fd83a9f7d`.

These are plan projections, not record-build authority. Task 2 and Task 6 must
observe and independently pin each profile after the pending predecessor gate is
complete. Any changed predecessor offset must change the projected branch bytes and
must be reviewed rather than normalized.

Starting from the current configuration, the structural projection is functions
`663 -> 664`, patch sites `612 -> 613`, and relocated leaves `94 -> 95`. Starting
from the current 957-region canonical manifest, splitting one official region into
two and appending one alignment plus one source leaf projects 960 regions. Exact
ownership arithmetic projects `+34` source bytes, `+34` generated bytes (32-byte
patch plus two-byte alignment), `-32` opaque bytes, and `+36` package bytes. Emitted
reports, not these projections, are the final authority.

## Task 0: Capture the post-varint32 clean regression boundary

**Files**

- Add a skip-string regression-baseline record under `openCFW/docs/research/`.
- Reuse or extend the existing exact unittest-identity evidence tooling only as
  required to make the new baseline fail closed.
- Do not modify production source, fixtures, overlay configuration, manifest, or
  provenance.

1. Wait for the varint32 Task 9 Apple and exact-root Linux full-discovery gates,
   their independent audit, and the final clean reviewed commit. Record that commit
   as `PROMOTION_BASE`; do not use this plan commit or an in-progress Task 9 commit.
2. From clean outputs on each profile, capture `./make.sh source`,
   `./make.sh verify`, `make vendor-snapshots`, the focused nanopb/profile suite,
   and `python3 -m unittest discover -s tests -v`. Record command, exit status,
   log byte size/SHA-256, compiler identity, artifact pins, and exact failure,
   error, and skip identities.
3. Require the existing skip-string candidate suite to be green and still
   production-excluded. There is no legitimate missing-source RED at this boundary;
   Task 1 creates the production RED by changing the contract first.
4. Make identity comparison fail closed on malformed logs, duplicate headings,
   inconsistent summaries, one synthetic new failure, and one synthetic new error.
   Platform-specific buffering may require an authenticated parser per profile, but
   it must reconcile exact heading sets and trailer counts rather than compare only
   totals.
5. Confirm two clean builds are byte-identical within each profile and that
   `git diff --check`, `git diff --cached --check`, and `git status --short` are
   clean before the first production test edit.

Commit: `test: pin nanopb skip-string regression boundary`.

## Task 1: Define the production and integration RED

**Files**

- Rename/transform
  `openCFW/tests/test_runtime_nanopb_skip_string_candidate.py` to
  `openCFW/tests/test_runtime_nanopb_skip_string_production.py`.
- Rename and expand the host fixture under `openCFW/tests/fixtures/`.
- Do not yet rename candidate source/header or modify `overlay.json`.

Change the test contract first and preserve a focused RED caused by missing
production source/registration. Require:

- production files `runtime_nanopb_skip_string.c` and `.h`, production symbol
  `open_cfw_nanopb_skip_string`, altered-source Zlib attribution, and absence of
  `_candidate` spellings from every production registration;
- the exact upstream, stock, caller, adjacent-boundary, ingress, outgoing-call,
  ABI, and bootloader pins above;
- exactly one new four-byte-aligned relocated leaf with two strict
  `target_function` calls, exactly one full-span patch, and exact projected count
  deltas from the actual Task 0 base;
- a complete `B.W` plus fourteen-NOP replacement, decoded target equality,
  unchanged caller, and no branch or stored pointer to relocated-leaf interior or
  alignment;
- deterministic production object/text/exidx qualification, no writable allocation,
  no rodata, and no undefined symbol beyond the two named source providers; and
- candidate paths/symbols absent from production overlay registration while the
  existing candidate evidence remains readable. Manifest ownership and provenance
  registration are staged explicitly in Tasks 4 and 5, not asserted as Task 1
  GREEN conditions.

Design the module so missing production files do not fail `setUpClass` and turn the
whole module into errors. The focused Task 1 command must have zero errors, no
unexpected skips, and exactly this failure-identity set—no more and no less:

1. `test_production_source_exists (test_runtime_nanopb_skip_string_production.NanopbSkipStringProductionContractTests)`
   fails with `missing production source:
   components/shared/nanopb/runtime_nanopb_skip_string.c`;
2. `test_overlay_registers_leaf_and_full_span_patch (test_runtime_nanopb_skip_string_production.NanopbSkipStringProductionContractTests)`
   fails with `missing production overlay registrations:
   open_cfw_nanopb_skip_string, replace_nanopb_skip_string`; and
3. `test_real_provider_integration_matches_upstream (test_runtime_nanopb_skip_string_production.NanopbSkipStringProductionIntegrationTests)`
   fails before compilation with `missing production integration prerequisite:
   components/shared/nanopb/runtime_nanopb_skip_string.c`.

All retained upstream, stock, topology, candidate-object, and exclusion identities
must remain GREEN in the same command. Run the predecessor candidate module before
renaming and preserve its GREEN log; run the transformed module afterward and hash
the exact three-failure RED log. Full discovery at this test-only commit may differ
from Task 0 only by those three added failure identities and the mechanical renamed
test identities; it must add no error. The active aggregate/current-consumer build
gates still describe the unchanged predecessor artifacts and must remain GREEN.

The completed contract must independently reject the following plausible mistakes
with exact failure messages. Task 1 authors the mutation cases but its allowlisted
run remains exactly the three missing-implementation identities above; Task 3
executes every mutation after a valid positive control exists:

1. a four-byte-only patch that leaves 28 stock bytes executable;
2. `BL` instead of non-linking `B.W` at the stock entry;
3. fixed `target_address` relocations to `0x0048F5AE` or `0x0048F3BE`;
4. decode/read providers swapped, one call omitted, or one extra undefined symbol;
5. a partial/shifted stock span or hash for concatenated adjacent bytes;
6. a leaf registered without a patch, or a patch without a leaf;
7. a second leaf or patch for `pb_skip_field()`; and
8. writable data, a `"size too large"` closure, or an unreviewed compiler profile.

The official-manifest-residue RED is deliberately not part of Task 1: the
predecessor manifest correctly owns all 32 bytes as official. Task 4 introduces and
closes that ownership assertion after the source/overlay implementation exists.

### Integrated behavior contract

Extend the fixture before implementation so the eventual GREEN path compiles the
production skip-string leaf with the real source-owned public varint32 and read
providers, not only seam stubs. Compare it with pristine authenticated
`pb_skip_field(stream, PB_WT_STRING)` for:

- empty payload, one-byte and multibyte lengths, length 127/128 boundaries, zero
  and `UINT32_MAX` direct seam cases;
- truncated length at every byte, fifth-byte overflow and extension overflow,
  truncated payload at every byte, payload exactly equal to `bytes_left`, and
  payload shorter/longer than the remaining budget;
- injected callback failure during length and payload reads, sticky first-error
  preservation, callback call count/position, consumed bytes, final `bytes_left`,
  state pointer, and error classification;
- decode failure short-circuiting with no read call; and
- successful forwarding of `NULL` destination and the lossless 32-bit length to
  `open_cfw_nanopb_read`.

Keep hand-written expected results beside the differential oracle. The untouched
stock dispatcher/caller must be checked structurally in the built component; host
tests do not claim execution of the relocated target branch.

Commit the test/fixture RED only:
`test: define nanopb skip-string production contract`.

## Task 2: Promote the source leaf and Apple overlay

**Files**

- Rename candidate source/header to production names and symbols.
- Modify `openCFW/components/apollo_main/core_overlay/overlay.json`.
- Modify the production test/fixture only to record reviewed output pins and satisfy
  the already-failing contract.

1. Preserve the qualified two-call algorithm, shared stream ABI, static width
   assertions, license, and compatibility caveat while removing all candidate seam
   names.
2. Register one strict relocated leaf after the current public varint32 leaf. Bind
   offset `+0x08` to `open_cfw_nanopb_decode_varint32` and offset `+0x14` to
   `open_cfw_nanopb_read`, both by exact `target_function`.
3. Register one 32-byte patch at `0x0048F64C`, authenticated by stock SHA-256
   `03afe2d6...`, branch type `b_w`, target
   `open_cfw_nanopb_skip_string`.
4. Build the overlay directly twice with Apple Clang 21.0.0. Pin renamed
   source/header/full object, text, symbols, both relocations, alignment, exidx
   disposition, linked bytes, source placement, entry replacement, overlay, and
   component. Package, manifest, report, and flash-plan pins remain Task 4 work.
   Record observed values if any projection differs.
5. Run production behavior, real-provider integration, stock/caller topology, and
   the adjacent varint32, read, and skip-varint focused tests that do not consume
   manifest/package/current-provenance pins. The exact three Task 1 RED identities
   must now be GREEN. Do not modify manifest/provenance/current-documentation
   consumers owned by later tasks merely to hide their expected RED.

Do not commit. Preserve focused GREEN logs and continue in the same working tree to
Task 3. Any failure outside current manifest/provenance/aggregate pins is a blocker,
not an expected downstream RED.

## Task 3: Make real-builder mutations fail closed

**Files**

- Expand `test_runtime_nanopb_skip_string_production.py` with temporary real-config
  mutation fixtures.
- Modify builder tests only if a general invariant is missing; do not weaken an
  existing builder guard.

Before any manifest edit, invoke the real overlay builder on the unmodified config
as a positive control and on independent temporary mutations for every Task 1
negative. Also reject wrong source/header hash, wrong text section, relocation
offset/type/symbol/binding drift, swapped providers, missing strict-relocation flag,
extra allocated section, non-CANTUNWIND companion, patch overlap, wrong stock hash,
and reordered/non-deterministic tail placement.

Each mutation must fail for its intended guard, not merely an earlier unrelated pin.
Where practical, temporarily update downstream aggregate pins so the mutation reaches
the targeted validation layer. Preserve exact RED output for at least the fixed-
address dependency and incomplete-patch cases, then rerun the unmutated builder
GREEN.

Do not commit. All positive focused gates must be GREEN and the negative mutation
set must fail for its exact expected messages. Continue in the same working tree to
Task 4.

## Task 4: Split manifest ownership and prove reversibility

**Files**

- Modify `openCFW/manifests/g2-2.2.6.10-core-source.json`.
- Modify active manifest/build-report/flash-plan consumers found by exact search.
- Extend the production suite's ownership tests before editing the manifest.

Add the ownership RED first. Its sole expected transient failure identity is
`test_manifest_splits_stock_span_and_appends_leaf (test_runtime_nanopb_skip_string_production.NanopbSkipStringProductionOwnershipTests)`;
it must report that the predecessor 382-byte region is still `official_blob`. It
must produce no error and must not cause any other focused identity to fail. Do not
commit this RED.

Replace only the 382-byte official region described above with the exact
generated-32/official-350 split and append independently named alignment and
source-compiled leaf records at the Apple builder-emitted component offsets.
Require:

- continuous, overlap-free, gap-free tiling of the full component;
- exact address/file-offset correspondence and output identities;
- no official byte inside `[0x0048F64C,0x0048F66C)`;
- the 350-byte official remainder and all bootloader ownership unchanged;
- rollback of the entry patch and removal of the appended tail recreating the exact
  predecessor component and package;
- exact report/manifest/flash-plan census and ownership totals from emitted output,
  not hand-edited arithmetic; and
- no broad pristine `pb_decode.c` object in any production artifact.

Starting from the current 957-region base, 960 is the expected canonical region
count if no preceding count changes. Treat a different Task 0 base as a reason to
recalculate and review, not to hard-code 960 blindly.

Turn the exact ownership RED GREEN, build the package twice, and pin the canonical
manifest, package, report, flash-plan, census, and ownership outputs. Do not commit:
the existing exact nanopb production allowlist/provenance consumers are expected to
recognize the new thirteenth leaf only after Task 5. Continue in the same working
tree. No manifest/ownership identity may remain RED when Task 5 begins.

## Task 5: Extend provenance and current documentation

**Files**

- Modify `openCFW/third_party/nanopb/PROVENANCE.json`.
- Modify `openCFW/third_party/nanopb/verify_snapshot.py`.
- Modify `openCFW/tests/test_nanopb_snapshot.py`.
- Promote the candidate audit to
  `openCFW/docs/research/nanopb-skip-string-source-audit.md`.
- Modify relevant NOTICE/EVIDENCE files, nanopb README, component/top-level
  READMEs, `docs/memory-map.md`, `docs/source-coverage.md`,
  `docs/upstream-inventory.md`, and `docs/linux-reproducible-build.md` only where
  exact search shows an active current consumer.

Add the provenance/snapshot RED first. Its sole expected transient failure identity
is
`test_skip_string_production_record_is_exact (test_nanopb_snapshot.NanopbSnapshotTests)`,
which must report the missing bounded production record; it must not be committed
RED. At this uncommitted checkpoint, direct `make nanopb-snapshot` or
`make vendor-snapshots` is also expected to stop only with
`nanopb production leaf set is not exact` because the overlay has thirteen leaves
and provenance still has twelve. Record that exact command-level RED; any other
verifier message is out of scope. Extend the exact nanopb production set from 12 to
13 functions and require a bounded skip-string record containing the three
release definition pins, altered local source/header pins, stock/caller/dependency
closure, source-to-source relocations, patch and manifest regions, Apple object and
artifact pins, bootloader exclusion, point-release caveat, and hardware deferral.

Negative fixtures must independently reject mutations of release/span/hash,
source/header hash, stock span/hash, caller encoding, either provider, either
relocation binding, patch shape, manifest split, license, compatibility-vs-exact-
release wording, bootloader scope, and evidence-file pin. Keep phase-local historical
artifact tables labeled historical; update only claims presented as current.

Run JSON parsing, snapshot verifier and negative fixtures, Apple `source`/`verify`,
vendor snapshots, production/manifest/core-overlay tests, and every current aggregate
consumer found by `rg`. Run full discovery and the Task 0 identity comparison. The
three Task 1 committed RED identities, the Task 4 ownership RED, and the Task 5
provenance RED must all be resolved; there must be zero new failure/error identities.
Two clean Apple builds must reproduce byte-for-byte.

Only now commit the complete Tasks 2-5 production range atomically:
`feat: promote and own nanopb skip-string leaf`. No production commit is permitted
before this GREEN boundary.

## Task 6: Record and verify exact-root Linux output

Use the reviewed `opencfw-linux-llvm` environment with exact source root
`/Users/kalani/Repo/SybilSightABCD/openCFW`, compiler
`/home/linuxbrew/.linuxbrew/bin/clang` version 22.1.8,
`OPENCFW_TOOLCHAIN_PROFILE=linux-clang`, Git-normalized file modes, no inherited
`GIT_DIR`/`GIT_WORK_TREE`, and a writable temporary directory.

Add failing Linux assertions first. Use the documented `--record-profile` overlay
and package commands, review every recorder change, and discard unrelated churn.
Independently pin two deterministic compilations, full object, text, symbols,
relocations, exidx, absence of data, alignment, linked leaf, placement, entry patch,
overlay, component/provider, package, reports, flash plan, manifest census,
ownership, compiler identity, and exact source-root spelling. Never copy Apple pins
into the Linux profile even if emitted bytes happen to match.

Then rerun without recording:

```sh
./make.sh source
./make.sh verify
make vendor-snapshots
python3 -m unittest -v \
  tests.test_runtime_nanopb_skip_string_production \
  tests.test_runtime_nanopb_decode_varint32_production \
  tests.test_runtime_nanopb_decode_varint_production \
  tests.test_runtime_nanopb_read \
  tests.test_runtime_nanopb_skip_varint_production \
  tests.test_nanopb_snapshot \
  tests.test_toolchain_profiles
```

Exercise Linux real-builder mutations, including provider swaps and fixed-address
dependencies, and update every active current Linux aggregate consumer found by
exact search while preserving historical milestones.

Commit: `test: reproduce nanopb skip-string on Linux`.

## Task 7: Independent whole-tranche reviews

After Tasks 0-6 are green, dispatch at least two independent reviewers against
`PROMOTION_BASE..HEAD`, not isolated commits:

1. The specification/evidence reviewer must inspect official and upstream bytes,
   0.4.7-0.4.9 identity, ABI guard elimination, complete stock and adjacent spans,
   sole caller and all ingress scans, both outgoing dependencies, bootloader
   exclusion, full patch, real-provider integration, manifest tiling/reversibility,
   provenance, Apple/Linux output, compatibility caveat, and hardware deferral.
2. The code/build-quality reviewer must inspect decode-failure short circuiting,
   length forwarding, `NULL` buffer, callback/error/budget behavior, shared ABI,
   exact section/relocation closure, `target_function` enforcement, CANTUNWIND
   disposition, branch range and NOP fill, deterministic tests, real-builder mutation
   non-vacuity, profile-test non-vacuity, and unrelated-diff contamination.

Resolve every Critical or Important finding and return the entire revised range to
the same reviewer. Record reviewer identity, reviewed commit, finding disposition,
and re-review result in a skip-string implementation log. Reviews are evidence
gates, not substitutes for executable tests.

## Task 8: Final zero-new-regression gate

Run fresh Apple and exact-root Linux gates from clean build outputs:

```sh
./make.sh source
./make.sh verify
make vendor-snapshots
python3 -m unittest -v \
  tests.test_runtime_nanopb_skip_string_production \
  tests.test_runtime_nanopb_decode_varint32_production \
  tests.test_runtime_nanopb_decode_varint_production \
  tests.test_runtime_nanopb_read \
  tests.test_runtime_nanopb_skip_varint_production \
  tests.test_nanopb_snapshot \
  tests.test_toolchain_profiles
python3 -m unittest discover -s tests -v
git diff --check
git diff --cached --check
git diff --check "$PROMOTION_BASE"..HEAD
git status --short
```

Hash every log and compare exact failure/error identities with Task 0 separately per
profile. Completion requires:

- zero new failure or error identities;
- every skip-string production, integrated behavior, artifact, ownership, snapshot,
  mutation, and Apple/Linux profile gate GREEN;
- two byte-identical output builds within each profile;
- the sole stock caller still entering the complete generated redirect;
- both linked calls resolving to source-owned providers by name;
- only planned files changed and every diff check clean; and
- both independent reviewers approving the final revised range.

Do not use `python3 -m unittest discover -v`; in this repository it can run zero
tests because `tests/` is not a package. Do not accept a reduced failure count
without exact identity comparison, and do not describe expected skips as passes.

The final report must state that no signing, flashing, reset, boot, display, radio,
power, or on-device behavior was exercised or proven. Hardware validation is a
separately authorized follow-up. It must also repeat that nanopb 0.4.9 is the
selected compatibility baseline, not an unequivocally recovered vendor point
release.

## Follow-on boundary

After this leaf is green, select the next independently closed nanopb function from
the audited frontier. Do not fold `pb_skip_field()`, `pb_decode_tag()`, signing,
flashing, or hardware testing into this tranche. Any follow-on that calls varint32,
read, or skip-string must bind source-owned providers by function name and must
capture its own clean regression boundary.
