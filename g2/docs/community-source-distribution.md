# Vendor-byte-free G2 community distribution

SPDX-License-Identifier: MIT

The distributable community artifact is a deterministic ZIP containing source,
license texts, overlay recipes, build adapters, and manifests. It contains no
official G2 package, component payload, compiled overlay, object, archive,
flash image, or EVENOTA file.

The repository's private build recipe uses some exact stock instruction bodies
as patch guards. The public bundle rewrites every such Apollo patch and literal
guard to an exact byte count plus SHA-256 digest. During a local hydrated build,
the builder reads those bytes from the recipient's authenticated official
package and verifies the digest before changing them. The archive therefore
does not carry the stock bodies merely to prove that a local input matches.

The archive root includes the project `LICENSE`, `NOTICE`, and `README.md`.
This keeps the MIT grant and the mixed-license notice alongside every extracted
copy instead of relying on a file outside the distributed artifact.

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
whose SHA-256 equals the official package or any of its six payloads.
It also rejects any continuous hexadecimal body of 128 bytes or more,
comma-separated dense byte transcripts, raw executable directives, and literal
hex/base64 decoder calls in component builders. A file-level notice that
forbids redistribution without a separate vendor agreement also fails closed;
the bundler never broadens it through a directory-level license. It
requires the sanitized Apollo recipe to contain no raw patch-site or literal
guard bytes. Bundle manifest schema 4 records the bounded stock-guard scope,
their `size-and-sha256-authenticated-local-base` representation, the captured
source closure, the repository-wide MIT/upstream policy receipt, and a
member-level license ledger covering every source-like archive member. That
ledger accepts a direct SPDX marker or one narrowly reviewed upstream root
bound to an exact included license artifact; unclassified project source fails
creation rather than inheriting a license from a directory name.
Component `EVIDENCE.md` ledgers are also excluded: they are private audit
chronology and can contain authenticated stock-body hex, not build inputs or
community-distributable clean-room source.
Verification also pins the manifest schema and local-package identity, requires
the declared member order and hashes exactly, and rejects duplicate or
case-colliding names, file/parent collisions, encrypted members, non-regular
types, traversal, backslashes, and symlink-derived archive members.
Member count, individual size, total uncompressed size, and archive size are
bounded before extraction. Creation captures selected source bytes once,
rechecks their inventory and byte closure before publication, writes through a
unique same-directory temporary file, verifies the finished bytes, and only
then atomically publishes them, with prior-output rollback on a failed final
readback. Verification and smoke extraction each operate
on one immutable in-memory snapshot rather than reopening a replaceable path.
Regular files use deterministic `0644` modes, while `g2/make.sh` is explicitly
stored as `0755`; verification rejects mode drift as well as type drift.
Production sources outside the broad component/vendor roots are followed
through repository-local quoted includes, recursively. The complete
`components/shared` clean-room candidate and typed-boundary source tree is
included even where a controller candidate is not yet production-routed; this
keeps the Touch, charging-case, GX8002, and EM9305 work available to the
community instead of reducing the archive to the currently linked Apollo
overlay. The corresponding Touch and charging-case host/runtime tests travel
with those candidates. The NemaVG stroke-cap candidate's host/Cortex-M55
semantic test and fixture also travel with its shared source. The link-complete
31-unit Touch Cortex-M0+ source-image
builder and FWPK packager are included as software-only, non-production-routed
artifacts. Sealed final classification ledgers travel with those sources. The
checkout's generated completion report is deliberately not copied into the
ZIP: `completion-assessment-check` must be current before creation, avoiding a
detached static progress claim in the public source archive.

The PT protocol community surface is census-pinned at 14 C units, 14 matching
headers, 13 runtime host suites, and six host fixtures, plus its bounded
in-place provider builder, provider admission test, and source summary. All 40
top-level board leaves are source-routed, but that does not make the board
dependency graph source-complete: the second-order boundary records 57
callable bindings (55 unique), of which 18 are source-routed and 39 are
retained (37 unique), plus 33 retained data addresses (23 SRAM, two immutable
flash, two callback entries, two external-XIP data, two XIP bounds, and two
MMIO). These authenticated boundaries remain deliberately supported and are
reported as `board_source_complete: false` rather than being hidden behind the
top-level route count.
The charging-case public surface includes the semantic-leaf, pure-helper, and
register-policy C/header pairs; their three runtime suites and host fixtures;
and each admission TSV and JSON summary. Their current status is described by
the charging-case final-classification summary.
The five-file charging-case Cortex-M0+ source-image package, its fail-closed
analyzer, focused host test, and summary are included as a software-only,
non-production-routed artifact. The extracted-tree smoke gate rebuilds and
checks that Case ELF/raw/EVEN package after donor hydration before building the
Apollo and bootloader overlays.
The semantic NemaVG start/end/coordinator stroke-cap C candidate, its host and
Cortex-M55 test, fixture, and sealed admission summary are also present; the
corpus-dependent admission analyzer remains excluded.
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

After extracting the community ZIP, the recipient runs:

```sh
cd openCFW-community/g2
python3 tools/community_distribution.py prepare-local \
  /private/path/to/official-s200_v2.2.6.10.evenota.bin \
  .
```

The command accepts only the exact 4,301,227-byte package with SHA-256
`f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`.
It then validates the EVENOTA structure and all six component sizes and hashes
before writing them into that recipient's local workspace. Hydration rejects
symlinked workspace paths and special-file targets. It also
recreates validated configured include directories that may be intentionally
empty in the ZIP; the actual local headers remain part of the audited recursive
source dependency closure. Provider writes use unique atomic staging and are
read back before the receipt-last `.open-cfw-local-hydration.json` is written.
If any provider or receipt write fails, the provider set rolls back to its prior
byte identities and the stale receipt remains absent. No
network fetch, signing, flashing, or hardware access occurs.

From the hydrated local workspace, the software-only build sequence is:

```sh
python3 components/bootloader/core_overlay/build_component.py
python3 components/apollo_main/core_overlay/build_component.py
python3 tools/open_cfw.py build \
  --manifest manifests/g2-2.2.6.10-core-source.json \
  --output-dir build/source \
  --toolchain-profile apple-clang
python3 tools/open_cfw.py verify-artifacts \
  --manifest manifests/g2-2.2.6.10-core-source.json \
  --output-dir build/source \
  --toolchain-profile apple-clang
```

The resulting firmware contains locally supplied official bytes and therefore
is not covered by the source bundle's redistribution statement. The ordinary
`source-release` command remains blocked until the repository records durable
redistribution authority for all six binary payloads.

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

It creates the vendor-free bundle and byte-identical local reference package,
extracts the bundle into an isolated temporary directory, hydrates it through
the same authenticated six-provider path, builds both overlays, assembles and
verifies the source package and every managed artifact, reports its identity
and flash-plan counts, and
then removes the temporary workspace. It never signs, flashes, or contacts
hardware.
