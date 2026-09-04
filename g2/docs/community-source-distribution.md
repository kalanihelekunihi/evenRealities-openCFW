# Official-payload-free G2 community distribution

SPDX-License-Identifier: MIT

The distributable community artifact is a deterministic ZIP containing source,
license texts, overlay recipes, build adapters, and manifests. It contains no
official G2 package, component payload, compiled overlay, object, archive,
flash image, or EVENOTA file.

## Public-export boundary

> **Release warning:** The ZIP created and verified by this workflow is the
> official-payload-free, history-free public artifact. The existing Git history
> retains 52 `g2/.tmp-*` paths and descendants totaling 108,601,986 bytes,
> including official-derived firmware variants. That set contains the
> now-deleted exact official-payload copies
> `g2/.tmp-pt-working-base.bin` and
> `g2/.tmp-pt-working-base-linux.bin` (SHA-256
> `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`) and
> must not be published, mirrored, or used through a hosting service's automatic
> source archive as-is.

Publish only the verified ZIP, or import that ZIP into a separately created
history whose entire reachable object set is audited before publication.
Adding ignore rules prevents new accidents but cannot remove existing Git
objects. Rewriting the private development history requires separate
authorization; this workflow does not perform that rewrite.

The verified ZIP preflight rejects every `.tmp*` path component, the local
`.open-cfw-local-hydration.json` receipt, executable and firmware suffixes, and
the immutable SHA-256 identities of the six official payloads and their outer
package. Content identity is checked independently of member names, so merely
renaming an official payload or giving it a source-looking suffix cannot admit
it. Hashes retained as authentication contracts are not payload bytes and do
not grant redistribution rights.

Here, **official-payload-free** means the archive contains no complete official
package or component and no unreviewed raw or encoded retained executable-byte
transcript. Exact hashes and reviewed semantic source tables are evidence and
source, not payload bodies; accepted numeric source tables are bound to exact
element-count and SHA-256 receipts so additions, omissions, or mutations fail
closed.

This is a source-only distribution statement. Once a recipient hydrates an
extracted tree, that tree, its hydration receipt, all provider files, and every
locally built firmware/package are outside this statement. The project has not
authorized public redistribution of those binaries. Hardware qualification is
blocked by unavailable physical evidence; the ZIP and software-only smoke gate make no
claim that any generated firmware has passed device qualification.

The current 166-input assessment records `source_complete=false`,
`release_authorized=false`, `hardware_operations=[]`, and six unresolved
binary redistribution authorities. Canonical Apple accounting is 574,315
production-source, 414,650 generated/reconstructible, 29,396
candidate-not-routed, 3,731,475 retained/external, and zero unclassified bytes
over a 4,749,836-byte payload and 4,750,780-byte outer package; 3,760,871 bytes
remain release-blocking. Canonical Linux accounting is 356,659
production-source, 331,912 generated/reconstructible, 29,396
candidate-not-routed, 4,031,853 retained/external, and zero unclassified bytes
over a 4,749,820-byte payload and 4,750,764-byte outer package; 4,061,249 bytes
remain release-blocking. The checked label reconciliations are 132,410 Apple
bytes and 3,346,976 Linux bytes. The source audit reports 930 distributable files
with zero errors, while the project-wide MIT/upstream normalization census
covers 919 targets. These metrics describe the hybrid source-overlay boundary;
they do not expand the source-only archive into a binary redistribution grant.

The repository's private build recipe uses some exact stock instruction bodies
as patch guards. The public bundle rewrites every such Apollo patch and literal
guard to an exact byte count plus SHA-256 digest. During a local hydrated build,
the builder reads those bytes from the recipient's authenticated official
package and verifies the digest before changing them. The archive therefore
does not carry the stock bodies merely to prove that a local input matches.

The archive root includes the project `.gitignore`, `LICENSE`, `NOTICE`, root
`Makefile`/`make.sh` G2 entrypoint, a G2-specific `README.md`,
`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, and `SUPPORT.md`. This
keeps the supported local workflow, donor/build-state exclusions, MIT grant,
mixed-license notice, contribution rules, conduct expectations,
security-reporting boundary, and support route alongside every extracted copy
instead of relying on files outside the distributed artifact. The root README
is sourced from `g2/docs/community-archive-README.md` rather than copying the
full-checkout README with unavailable R1 and private-research links. The exact
`.gitignore` bytes are authenticated by the bundle inventory and classified as
MIT project infrastructure in the member-level license ledger. A recursive
Markdown link-closure check rejects missing, escaping, or unsafe local targets
during both creation and verification; URL fragments are deliberately
normalized to their containing file for this member-closure check.

Create and verify it locally with:

```sh
cd g2
make community-source-bundle
```

`tools/community_distribution.py` generates a content-addressed
`BUNDLE-MANIFEST.json`, uses uncompressed ZIP storage plus fixed timestamps and
modes for cross-Python reproducibility, rejects `blobs/`
and all `build`/`build-*`/temporary output directories at any depth, rejects
firmware/object/archive suffixes, and rejects any member
whose SHA-256 equals the official package or any of its six payloads. Those
seven denial identities and the six component name/kind/path/size/hash tuples
are immutable constants checked against the local base manifest, rather than
being trusted solely from mutable manifest content.
It also rejects any continuous hexadecimal body of 128 bytes or more,
comma-separated dense byte transcripts, decimal/numeric byte arrays in
C/C++/assembly, Python, or JSON, comment-separated C literal runs,
macro/character-literal initializers, wide assembly data directives, structured
JSON encoded chunks, split encoded string transcripts, and statically composed
Python decoder inputs. Reviewed semantic
numeric source tables require exact count-and-digest receipts. A file-level notice that
forbids redistribution without a separate vendor agreement also fails closed;
the bundler never broadens it through a directory-level license. All fifteen
known InvenSense EDMP payload/restricted-notice paths are also denied by exact
name, independently of content signatures, so rewriting a header without
removing the dependency cannot bypass the public boundary. The production
recipe retains the authenticated stock IMU donor object and selects none of
those implementation headers; only the upstream root license text is retained
as evidence/notice, and it does not authorize the excluded files. It
requires the sanitized Apollo recipe to contain no raw patch-site or literal
guard bytes. Bundle manifest schema 5 records the bounded stock-guard scope,
their `size-and-sha256-authenticated-local-base` representation, the captured
source closure, the repository-wide MIT/upstream policy receipt, and a
member-level license ledger covering every payload member. The generated
`BUNDLE-MANIFEST.json` envelope is project-authored MIT material under the
included root `LICENSE`; it cannot self-hash into its own ledger. Code, linker,
build-script, and patch source requires a direct SPDX marker or one narrowly
reviewed upstream root bound to an exact included license artifact. Exact
classes separately cover authenticated project infrastructure,
project documents/data, generated factual receipts, upstream provenance data,
and the license/notice evidence itself. Every row binds class, basis, license,
path, size, SHA-256, and evidence;
an unclassified payload member fails creation rather than inheriting a license
from a directory name. All eighteen included license-text members have
independent exact SHA-256 pins; a mutated, omitted, unused, or unrecognized
alternate license member fails closed. The CMSIS-FreeRTOS queue adapters bind
the included Arm Apache-2.0 text directly instead of borrowing an unrelated
component's Apache notice. The shared ring-buffer adaptation and eight
mpaland-derived formatting leaves likewise bind their exact included upstream
MIT license texts.
Component `EVIDENCE.md` ledgers are also excluded: they are private audit
chronology and can contain authenticated stock-body hex, not build inputs or
community-distributable clean-room source.
Verification also pins the manifest schema and local-package identity, requires
the declared member order and hashes exactly, and rejects duplicate or
case-colliding names, file/parent collisions, encrypted members, non-regular
types, traversal, backslashes, and symlink-derived archive members.
Member count, individual size, total uncompressed size, and archive size are
bounded before extraction. Verification reads through one no-follow file
descriptor, applies the archive-size cap before allocation, rejects hardlinked
or special input paths, and checks that descriptor identity and size remain
stable. Creation captures selected source bytes once,
rechecks their inventory and byte closure before publication, builds the ZIP in
an anonymous temporary file, then publishes through a no-follow
descriptor-bound same-directory temporary file only after re-authenticating the
expected prior output. JSON recipes, quoted-include discovery, hydration
targets, and output parents reject symlink or hardlink aliases. Verification
and smoke extraction each operate
on one immutable in-memory snapshot rather than reopening a replaceable path.
Regular files use deterministic `0644` modes, while `g2/make.sh` is explicitly
stored as `0755`; verification rejects mode drift as well as type drift.
Production sources outside the broad component/vendor roots are followed
through repository-local quoted includes, recursively. The complete
`components/shared` clean-room candidate and typed-boundary source tree is
included even where a controller candidate is not yet production-routed; this
keeps the Touch, charging-case, GX8002, and EM9305 work available to the
community instead of reducing the archive to the currently linked Apollo
overlay. That tree now includes the FTL-licensed FreeType 2.9.1 CFF policy
adapter and its sealed admission receipt. The receipt authenticates 47 mapped
stock functions / 12,062 bytes and the 17-file upstream CFF inventory, while
recording no authenticated stock policy callsite, no target placement,
`stock_image_overlay_routed=false`, and no hardware operation. The
mapping tables derive from private corpus evidence; those inputs and the
repository admission analyzer remain repository-only. The public archive does
not turn this software admission into an IAR placement or live-rendering claim.
The corresponding Touch and charging-case host/runtime tests travel with those
candidates. The NemaVG stroke-cap host/Cortex-M55 semantic test and fixture also
travel with its shared evidence source. All three
no-argument/global-context start/end/coordinator entries are production-routed;
no stroke-cap stock entry remains unpatched or candidate-only
boundaries because their exact ABI, MVE/stack construction, and lower helpers
are not sufficiently recovered. The link-complete
31-unit Touch Cortex-M0+ source-image
builder and FWPK packager are included as software-only, non-production-routed
artifacts. Sealed final classification ledgers travel with those sources. The
included
`tools/manifests/g2-touch-final-source-candidate-provenance.tsv` partitions
Touch's 14,510 candidate stock-address bytes into six mixed-license,
semantic-only provenance rows. Every row records
`production_elf_ownership=false`; together with 512 generated, 19,442
retained/external, and zero unclassified Touch bytes, this is an evidence
boundary rather than a production-source or stock-byte redistribution claim.
The persisted EM9305
[final-readiness ledger](../tools/manifests/em9305-final-source-readiness.tsv)
likewise carries classification evidence, not controller bytes: it accounts
for all 175 residual spans /
33,658 bytes as 23 spans / 1,240 bytes of concrete but unrouted source, 25 /
8,348 bytes of typed unsupported external boundary, and 127 / 24,070 bytes of
unavailable proprietary controller code. Zero residual bytes are unclassified,
but EM9305 remains `source_complete=false`, stock-retained, and outside public
binary redistribution authority.
The archive also carries machine-readable readiness and attribution evidence
for its public source surfaces, together with the deterministic completion
assessment triplet. Creation requires `completion-assessment-check` to be
current first, so the included assessment is bound to the selected evidence
rather than presented as a detached progress claim.

The PT protocol community surface is census-pinned at 15 C units and 14
headers, 29 source files total: 28 independently authored MIT inputs plus the
separately attributed Apache-2.0 Google/liblc3 encoder-setup adaptation. The
linked provider records the aggregate SPDX expression `MIT AND Apache-2.0`.
Its analyzer link contains 21,466 text bytes and 1,177 read-only-data bytes,
22,643 loadable bytes total; the bounded in-place provider is 22,696 loadable
bytes. The surface also carries 13 runtime host suites and six host fixtures,
plus its bounded in-place provider builder, provider admission test, and source
summary.

All 40 top-level board leaves are source-routed, but that does not make the
board dependency graph source-complete: the second-order boundary records 81
callable bindings, of which 68 are source-routed (29 overlay and 39 local) and
13 are retained, plus 97 retained data bindings at 94 unique addresses. The
four fixed LC3 contexts are authenticated at consecutive `0xA44` strides, and
the unrelated byte-state/allocation boundary immediately after the fourth is
another `0xA44` later. Each context has a `0x1C`-byte header and 2,600 bytes of
encoder storage. Every
supported duration/rate configuration is host-tested, and the bounded entry
rejects an oversize geometry before writing. Runtime-provided configuration
values remain statically unproven, but they are no longer a memory-safety gap.
These authenticated boundaries remain deliberately supported and are reported
as `board_source_complete: false` rather than being hidden behind the
top-level route count. Hardware validation is blocked by unavailable physical evidence.
The charging-case public surface includes the semantic-leaf, pure-helper, and
register-policy C/header pairs; their three runtime suites and host fixtures;
and each admission TSV and JSON summary. Their current status is described by
the charging-case final-classification summary.
The five-file charging-case Cortex-M0+ source-image package, its fail-closed
analyzer, focused host test, and summary are included as a software-only,
non-production-routed artifact. The extracted-tree smoke gate rebuilds and
checks that Case ELF/raw/EVEN package after donor hydration before building the
Apollo and bootloader overlays.
The semantic NemaVG stroke-cap evidence C, the reviewed three-entry production
source, its host and Cortex-M55 test, fixture, and sealed admission summary are
also present. The summary records three routed functions / 6,614 stock bytes
and zero unpatched endpoint candidates. Bundle creation and verification
cross-bind the reviewed production source identity and all three exact routes,
reject the private integrators, and keep the semantic evidence source isolated as
non-routed evidence; the corpus-dependent admission analyzer remains excluded.
This distribution guide is the public documentation for those source surfaces.
The evidence-oriented analyzers, extractors, decompilation corpus, and research
notes used to derive the summaries are deliberately excluded. One MIT FreeRTOS
scheduler trio is already production-routed but still lives under the checkout's
research directory; the bundler copies only that C/header pair to the public
core-overlay path and rewrites the bundled recipe accordingly. No `research/`
path is emitted.

Every member must be UTF-8 source/documentation without NUL bytes or private-key
blocks. Common credential/key filenames and suffixes are rejected. Verification
recursively parses every bundled JSON document and rejects any `expected_hex`
or `target_expected_hex` key. The sanitized build recipes retain only byte count
and SHA-256 contracts: these authenticate bytes in the user's local official
package but cannot reconstruct or redistribute those bytes.

## Local user workflow

The recipient must obtain the official `s200_v2.2.6.10` G2 package through a
channel available to them. The project does not redistribute it or infer that
possession grants further distribution rights.

The extracted build requires Python 3.9 or newer, GNU Make, and one compiler
whose first version line matches the recorded `apple-clang` or `linux-clang`
profile. Check those dependencies before writing local official payloads:

```sh
cd openCFW-community
./make.sh g2-community-preflight
```

The command also verifies that the selected Clang builtin-resource include
directory exists. It performs no network, hydration, build, signing, flashing,
or hardware operation. `OPENCFW_CLANG` and `OPENCFW_TOOLCHAIN_PROFILE` select an
explicit reviewed pair; a missing compiler, unknown profile, version mismatch,
non-GNU Make, or missing resource directory fails immediately.
Export the same overrides for both preflight and build because preflight reports
but does not persist environment selections. Set `OPENCFW_MAKE=gmake` on hosts
where GNU Make is installed under that name.

After extracting the community ZIP, the recipient runs:

```sh
cd openCFW-community/g2
python3 tools/community_distribution.py prepare-local \
  /private/path/to/official-s200_v2.2.6.10.evenota.bin \
  .
```

The command accepts only the exact 4,301,227-byte package with SHA-256
`f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`.
It then validates the EVENOTA structure and all six immutable component
name/kind/path/size/hash contracts before writing them into that recipient's
local workspace. Hydration rejects
symlinked workspace paths and special-file targets. It also
recreates validated configured include directories that may be intentionally
empty in the ZIP; the actual local headers remain part of the audited recursive
source dependency closure. Provider writes use unique atomic staging and are
descriptor-read back before the receipt-last `.open-cfw-local-hydration.json`
is written.
If any provider or receipt write fails, the provider set rolls back to its prior
byte identities and the stale receipt remains absent. No
network fetch, signing, flashing, or hardware access occurs.
The bundled `.gitignore` keeps all six hydrated provider paths, the hydration
receipt, build trees, nested temporary paths, and canonical lock files out of a
new Git index while leaving source, policy, and `PROVENANCE.md` files addable.
This is an accident-prevention layer for a clean extracted tree, not permission
to publish a hydrated tree or a substitute for auditing every reachable object
in any new public history.

From the hydrated local workspace, the software-only build sequence is shown
below for the canonical Apple profile. The included Make entrypoint passes the
preflight-selected compiler and either reviewed profile consistently to both
component builders and the package assembler:

```sh
python3 components/bootloader/core_overlay/build_component.py
python3 components/apollo_main/core_overlay/build_component.py
python3 tools/open_cfw.py build \
  --manifest manifests/g2-2.2.6.10-core-source.json \
  --output-dir build/source \
  --toolchain-profile apple-clang
python3 tools/open_cfw.py verify \
  --manifest manifests/g2-2.2.6.10-core-source.json
python3 tools/open_cfw.py verify-artifacts \
  --manifest manifests/g2-2.2.6.10-core-source.json \
  --output-dir build/source \
  --toolchain-profile apple-clang
```

From the extracted archive root, `./make.sh g2-community-local-build` runs this
same bounded test/build/verify sequence through the included minimal dispatcher.
It does not expose full-checkout R1, research-corpus, publication, or canonical-
apply targets.

The resulting firmware contains locally supplied official bytes and therefore
is not covered by the source bundle's redistribution statement. Neither the
hydrated tree nor any locally generated firmware is a public artifact. The
ordinary `source-release` command remains blocked until the repository records
durable redistribution authority for all six binary payloads.

## Maintainer canonical-observation workflow

Ordinary community builds verify committed pins and cannot update them. When a
reviewed source or compiler change intentionally changes the Apollo core,
maintainers record two independent observations under each reviewed compiler.
Keep the source tree unchanged throughout all four builds, use four distinct
non-symlink output paths below the G2 root (not `/tmp` or another external tree),
and do not copy or hardlink one run's receipt or artifacts into another run:

### Isolate the reviewed Apple compiler

Strict admission requires every identity-bearing compiler and builtin header
to be a regular file with exactly one hard link. Apple/Xcode installations can
expose reviewed bytes through multiply linked filesystem entries, so do not
record directly from the vendor-installed Apple clang. Make a fresh,
byte-identical review copy below the G2 `build/` tree and copy its exact Clang
resource `include` closure into the location derived by that copied driver:

```sh
APPLE_CLANG_SOURCE="$(xcrun --find clang)"
APPLE_RESOURCE_SOURCE="$(
  "$APPLE_CLANG_SOURCE" --no-default-config -print-resource-dir
)"
APPLE_REVIEW_ROOT="$PWD/build/canonical-toolchain/apple-clang-review"
test ! -e "$APPLE_REVIEW_ROOT"
mkdir -p "$APPLE_REVIEW_ROOT/usr/bin"
APPLE_CLANG_REVIEW="$APPLE_REVIEW_ROOT/usr/bin/clang"
/bin/cp -p "$APPLE_CLANG_SOURCE" "$APPLE_CLANG_REVIEW"

APPLE_RESOURCE_REVIEW="$(
  "$APPLE_CLANG_REVIEW" --no-default-config -print-resource-dir
)"
case "$APPLE_RESOURCE_REVIEW/" in
  "$APPLE_REVIEW_ROOT/"*) ;;
  *) echo "copied clang resource directory escaped review root" >&2; exit 1 ;;
esac
mkdir -p "$APPLE_RESOURCE_REVIEW"
/bin/cp -R "$APPLE_RESOURCE_SOURCE/include" \
  "$APPLE_RESOURCE_REVIEW/include"

python3 - "$APPLE_CLANG_SOURCE" "$APPLE_RESOURCE_SOURCE/include" \
  "$APPLE_CLANG_REVIEW" "$APPLE_RESOURCE_REVIEW/include" <<'PY'
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import stat
import sys


def closure(root: Path, *, single_link: bool) -> tuple[list[dict[str, object]], int, str]:
    if root.is_symlink() or not root.is_dir():
        raise SystemExit(f"unsafe resource include directory: {root}")
    entries: list[dict[str, object]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            raise SystemExit(f"resource closure contains a symlink: {path}")
        if path.is_dir():
            continue
        metadata = path.lstat()
        if not stat.S_ISREG(metadata.st_mode):
            raise SystemExit(f"resource closure contains a special file: {path}")
        if single_link and metadata.st_nlink != 1:
            raise SystemExit(f"review copy is not single-link: {path}")
        payload = path.read_bytes()
        entries.append({
            "path": path.relative_to(root).as_posix(),
            "size": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        })
    encoded = json.dumps(
        entries, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return entries, sum(int(row["size"]) for row in entries), hashlib.sha256(encoded).hexdigest()


source_compiler, source_include, review_compiler, review_include = map(
    Path, sys.argv[1:]
)
source_payload = source_compiler.read_bytes()
review_payload = review_compiler.read_bytes()
review_metadata = review_compiler.lstat()
if not stat.S_ISREG(review_metadata.st_mode) or review_metadata.st_nlink != 1:
    raise SystemExit("review compiler is not a single-link regular file")
if source_payload != review_payload:
    raise SystemExit("review compiler bytes differ from selected Apple clang")
source_closure = closure(source_include, single_link=False)
review_closure = closure(review_include, single_link=True)
if source_closure != review_closure:
    raise SystemExit("review compiler resource-header closure differs")
print(f"compiler_size={len(review_payload)}")
print(f"compiler_sha256={hashlib.sha256(review_payload).hexdigest()}")
print(f"resource_header_entries={len(review_closure[0])}")
print(f"resource_header_total_size={review_closure[1]}")
print(f"resource_header_closure_sha256={review_closure[2]}")
PY

test "$(
  "$APPLE_CLANG_REVIEW" --no-default-config -print-resource-dir
)" = "$APPLE_RESOURCE_REVIEW"
```

Review the printed compiler and resource-closure hashes, keep this review tree
unchanged until admission completes, and use the same copy for both Apple
observations. Its local absolute path is receipt evidence, not a committed
machine-path pin. The `build/` review tree is outside the enumerated firmware
source closure. Copying reviewed bytes changes only their filesystem identity;
it does not authorize a source-closure or artifact change. Admission still
requires the current reviewed source digest, compiler/version pins, and
byte-reproducible Apple artifacts.

```sh
make core-canonical-observation \
  OPENCFW_CLANG="$APPLE_CLANG_REVIEW" \
  OPENCFW_TOOLCHAIN_PROFILE=apple-clang \
  CORE_CANONICAL_OBSERVATION_DIR=build/canonical-observation-g2-final97/apple-a
make core-canonical-observation \
  OPENCFW_CLANG="$APPLE_CLANG_REVIEW" \
  OPENCFW_TOOLCHAIN_PROFILE=apple-clang \
  CORE_CANONICAL_OBSERVATION_DIR=build/canonical-observation-g2-final97/apple-b
make core-canonical-observation \
  OPENCFW_CLANG=/path/to/reviewed/linux-clang \
  OPENCFW_TOOLCHAIN_PROFILE=linux-clang \
  CORE_CANONICAL_OBSERVATION_DIR=build/canonical-observation-g2-final97/linux-a
make core-canonical-observation \
  OPENCFW_CLANG=/path/to/reviewed/linux-clang \
  OPENCFW_TOOLCHAIN_PROFILE=linux-clang \
  CORE_CANONICAL_OBSERVATION_DIR=build/canonical-observation-g2-final97/linux-b
```

Each output directory contains its own `build-report.json` and the artifacts
authenticated by that report. A receipt records the reviewed compiler
identity, source-input closure, core stage, liblc3 and PT intermediate stages,
and final overlay/component artifacts. The admission tool requires the two
runs for a profile to be byte-for-byte reproducible, requires Apple and Linux
to describe the same source-input closure and distinct compiler identities,
rejects shared report/artifact inodes, and rejects restricted IMU source paths.
Distinct inodes prove separately supplied artifact generations and byte
reproducibility; they are not cryptographic attestation that two executions
occurred. Maintainers or CI remain responsible for actually running all four
builds.

Canonical compilation uses `-nostdinc`: it excludes ambient host include
directories and admits only the reviewed repository include paths plus the
explicit Clang builtin resource include directory. The observation receipt
binds the exact builtin-header closure used by the core, liblc3, and PT stages.

Admission intentionally does not auto-migrate the reviewed core-stage,
per-leaf, relocation/closure, in-place-data, compiler-identity, or liblc3 pins.
It authenticates the corresponding stage/intermediate evidence and requires
those pins to equal the current reviewed config; any drift is rejected for a
separate evidence review. Only artifact-proven final, PT, provider, package,
and manifest fields may change through this workflow. This is a maintainer
review/authorization boundary, not an unclassified or opaque firmware region.

The live provider tree normally contains the Apple bootloader. Build the
already pinned Linux bootloader into a separate path below the G2 root and pass
it explicitly when admitting the Linux profile:

```sh
python3 components/bootloader/core_overlay/build_component.py \
  --clang /path/to/reviewed/linux-clang \
  --toolchain-profile linux-clang \
  --output-dir build/canonical-provider/linux-clang/apollo_bootloader

LINUX_BOOT_PROVIDER=build/canonical-provider/linux-clang/apollo_bootloader/ota_s200_bootloader.bin
make core-canonical-admission \
  CORE_CANONICAL_APPLE_A=build/canonical-observation-g2-final97/apple-a/build-report.json \
  CORE_CANONICAL_APPLE_B=build/canonical-observation-g2-final97/apple-b/build-report.json \
  CORE_CANONICAL_LINUX_A=build/canonical-observation-g2-final97/linux-a/build-report.json \
  CORE_CANONICAL_LINUX_B=build/canonical-observation-g2-final97/linux-b/build-report.json \
  CORE_CANONICAL_PROFILE_PROVIDER_ARGS="--profile-provider linux-clang apollo_bootloader $LINUX_BOOT_PROVIDER"
```

`core-canonical-admission` is the mandatory no-write review pass. It validates
the observations, all selected profile providers, and the proposed config,
manifest, and Apple provider generation, then reports the verified source and
profile identities. Only after reviewing the four receipts and that result run
the same command as `core-canonical-apply`. Its explicit `--apply` path uses a
serialized, fail-closed transaction: it publishes the admitted Apple Apollo
provider, matching overlay, and normalized build-report commit marker first,
then the config, and finally the manifest as the public commit record. A caught
write or readback failure rolls all five paths back. The transaction is not
filesystem-atomic across process death; an interrupted run instead fails
closed as a detectable non-admitted mixed generation that a rerun can recover.
The Apple generation therefore does not need manual staging into the live
path. Normal pinned builds and tests must then reproduce both profiles.
These commands only read, compile, verify, and update local repository files.
They perform no network access, signing, flashing, or hardware operation.

### Rebuild post-apply dual-profile evidence

After `core-canonical-apply` succeeds, rebuild the admitted Apple provider and
independently reproduce the Linux provider. Use the same isolated Apple
compiler and reviewed Linux compiler that produced the admitted observations:

```sh
python3 components/apollo_main/core_overlay/build_component.py \
  --clang "$APPLE_CLANG_REVIEW" \
  --toolchain-profile apple-clang \
  --output-dir components/apollo_main/core_overlay/build
python3 components/apollo_main/core_overlay/build_component.py \
  --clang /path/to/reviewed/linux-clang \
  --toolchain-profile linux-clang \
  --output-dir .tmp-postapply-core-linux
cmp .tmp-postapply-core-linux/ota_s200_firmware_ota.bin \
  build/canonical-provider/linux-clang/apollo_main-final81/ota_s200_firmware_ota.bin
```

The live core-source manifest carries authenticated profile-specific provider
paths. `open_cfw.py` reads and reports those effective paths for Linux, so both
profiles use the same semantic manifest identity; a scratch manifest would
change that identity and correctly lose the checked ownership-authority
pointer.

Build, verify the six current providers and deterministic package, and then
verify the complete generated artifact set for each profile:

```sh
python3 tools/open_cfw.py build \
  --manifest manifests/g2-2.2.6.10-core-source.json \
  --output-dir build/postapply-package-apple \
  --toolchain-profile apple-clang
python3 tools/open_cfw.py verify \
  --manifest manifests/g2-2.2.6.10-core-source.json \
  --toolchain-profile apple-clang
python3 tools/open_cfw.py verify-artifacts \
  --manifest manifests/g2-2.2.6.10-core-source.json \
  --output-dir build/postapply-package-apple \
  --toolchain-profile apple-clang

python3 tools/open_cfw.py build \
  --manifest manifests/g2-2.2.6.10-core-source.json \
  --output-dir build/postapply-package-linux \
  --toolchain-profile linux-clang
python3 tools/open_cfw.py verify \
  --manifest manifests/g2-2.2.6.10-core-source.json \
  --toolchain-profile linux-clang
python3 tools/open_cfw.py verify-artifacts \
  --manifest manifests/g2-2.2.6.10-core-source.json \
  --output-dir build/postapply-package-linux \
  --toolchain-profile linux-clang
```

Only after all six commands succeed may a maintainer refresh the checked
ownership receipt through the explicit maintainer route:

```sh
make dual-profile-ownership-write
```

That target authenticates both A/B observation pairs, both boot providers, all
six exact providers in each post-apply package, and the current source closure
before atomically replacing the companion and verifying its readback. Ordinary
`make dual-profile-ownership` remains read-only and fails closed if the checked
receipt is missing, stale, redirected, or inconsistent with live evidence.

`.tmp-postapply-core-linux/`, the four canonical receipt trees under
`build/canonical-observation-g2-final97/{apple-a,apple-b,linux-a,linux-b}/`, and
both `build/postapply-package-*` directories are ignored, private local
evidence. They are not Git inputs or community-archive members. This entire
sequence is deterministic and software-only: it performs no network access,
signing, flashing, or hardware operation.

## Dual-profile ownership semantics

Do not use a flash-plan `address_status` value as exact byte ownership. The
address, component offset, size, digest, and target mapping in the plan are
authoritative. Ownership labels are a presentation map and require the checked
[`g2-dual-profile-ownership.json`](../tools/manifests/g2-dual-profile-ownership.json)
reconciliation. Only the exact authenticated Apple/Linux core-source package
and manifest identities name that companion in their `address_status_semantics`
objects. Other source-build manifests are explicitly marked unreconciled and
carry no inapplicable companion pointer; provider-only reference plans retain
authoritative provider-origin labels.

This distinction is material for `linux-clang`. The non-canonical layout
inherits coarse Apple region boundaries below the appended source tail. Its
plan-level Apollo labels read 207,195 source, 407,790 generated, and 3,226,807
retained bytes, but the separately admitted Linux component builders prove
207,141 source, 135,378 generated-addressed, 3,499,273 retained, and 32
component-container bytes. The checked reconciliation therefore moves 54
plan-labeled source bytes and 272,412 plan-labeled generated bytes back into
the authoritative count, closing a 272,466-byte retained-byte understatement.
Those coarse spans are explicitly typed `typed_mixed_profile_ownership`; no
complete per-byte source-versus-generated mask is claimed for them. Machine
readiness therefore records `per_byte_ownership_mask_complete=false` for
Linux. The canonical Apple component builder/region mask is the sole current
per-byte ownership authority; Linux ownership is intentionally limited to its
exact aggregate totals and the two typed-mixed spans.

The canonical Apple address labels also lag exact builder ownership by 17,800
bytes and are marked non-authoritative. Its checked component totals are
424,703 source, 425,806 generated-addressed, 3,198,967 retained, and 32
component-container bytes across Apollo main plus bootloader.

Across all six package payloads, the authoritative buckets are:

| Profile | Production source | Generated/reconstructible | Candidate, not routed | Typed retained/external | Unclassified | Payload | Internal component container | Outer EVENOTA envelope |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `apple-clang` | 424,703 | 426,474 | 30,636 | 3,795,983 | 0 | 4,677,796 | 300 | 944 |
| `linux-clang` | 207,141 | 136,046 | 30,636 | 4,096,289 | 0 | 4,470,112 | 300 | 944 |

Here, zero unclassified bytes means every byte has a source, generated,
candidate, retained/external, container, or explicit typed-mixed decision. It
does not mean the images are source-complete: all six binary redistribution
authorities remain unresolved, and the Linux typed-mixed spans do not carry a
per-byte ownership mask. Internal component container is an orthogonal location
count already included in the ownership buckets, not an additional byte bucket.
The public ZIP includes the checked companion, analyzer source, adversarial
verification test, and this interpretation guide. It intentionally excludes the
four local `build/canonical-observation/{apple-a,apple-b,linux-a,linux-b}/`
receipt trees and `build/postapply-package-*` artifacts, so it preserves the
exact proof receipt but cannot independently rerun the evidence audit. Inspect
the bundled receipt at
`g2/tools/manifests/g2-dual-profile-ownership.json`. In a full local checkout
that also holds the four admitted observations, both boot reports, and both
post-apply packages, rerun the evidence audit offline with:

```sh
cd g2
python3 tools/analyze_g2_dual_profile_ownership.py
```

## Extracted-tree smoke build

The workflow is repeated in a fresh extraction, not against the repository
checkout. The bootloader and Apollo builders, source-manifest assembly, package
verification, exhaustive managed-artifact ledger, Case source-image gate,
NemaVG runtime gate, and clock-divider runtime gate must all pass against the
current pinned hybrid profile. This is an offline build/verification exercise
only; no image is signed, flashed, publicly released, or executed on hardware.

The repeatable integration gate is:

```sh
cd g2
make community-source-smoke
```

It creates the official-payload-free bundle and byte-identical local reference package,
extracts the bundle into an isolated temporary directory, hydrates it through
the same authenticated six-provider path, builds both overlays, assembles and
verifies the source package and every managed artifact, reports its identity
and flash-plan counts, and
then removes the temporary workspace. It never signs, flashes, or contacts
hardware. Its internal temporary workspace uses the resolved physical system
temporary directory so the strict no-symlink path policy also works with the
standard macOS `/var` to `/private/var` alias.
