# G2 core-source release licensing and redistribution inventory

SPDX-License-Identifier: MIT

This inventory covers the six payloads assembled by
`manifests/g2-2.2.6.10-core-source.json`. It is not a repository-wide license
summary. In particular, a source-available replacement or overlay does not by
itself grant permission to redistribute the official firmware bytes retained
around it.

## Package artifact authority

| Payload | Provider in core-source | Source availability | Binary redistribution authority |
|---|---|---|---|
| codec | authenticated official blob | binary-only | unresolved; no Even/NationalChip redistribution grant is recorded |
| ble_em9305 | authenticated official blob | binary-only | unresolved; no Even/EM9305 redistribution grant is recorded |
| touch | authenticated official blob | binary-only | unresolved; no Even touch-firmware redistribution grant is recorded |
| case | authenticated official blob | binary-only | unresolved; no Even case-firmware redistribution grant is recorded |
| apollo_bootloader | source-built overlay over retained official bytes | partial source | unresolved for the retained Even bytes |
| apollo_main | source-built overlay over retained official bytes | partial source | unresolved for the retained Even bytes |

Consequently the current package may be built and analyzed privately, but the
repository does not establish authority to distribute it publicly. The
`source-release` entry point now fails before writing a release artifact. This
is an authority gate only; it does not assert that distribution is forbidden
under facts or agreements outside this repository.

The current 157-input completion assessment reports
`source_complete=false`, `release_authorized=false`, hardware validation
blocked by unavailable physical evidence, and `hardware_operations=[]`. Its canonical
Apple package contains 4,677,796 payload bytes (4,678,740 bytes with the
EVENOTA envelope), of which 3,826,619 are release-blocking. All bytes are
classified, but all six binary redistribution authorities in the table above
remain unresolved. The source audit independently reports 786 distributable
source files with zero metadata errors, and the project-wide MIT/upstream
normalization census covers 906 targets. None of those source results grants
permission to redistribute retained or binary-only firmware.

Older per-closure provenance manifests retain exact milestone package
identities. Their phrase “complete firmware package” means that all package
container parts were assembled at that milestone; it is not a source-complete,
current-package, hardware-qualified, or redistribution-authorized claim. The
checked assessment and authority gate above remain the live release boundary.

The persisted EM9305
[final-readiness ledger](../tools/manifests/em9305-final-source-readiness.tsv)
accounts for all 175 residual spans / 33,658 bytes with zero unclassified spans
or bytes. It separates 1,240
bytes of concrete but unrouted source from 8,348 bytes of typed unsupported
external boundary and 24,070 bytes of unavailable proprietary controller code.
That receipt closes classification, not source or licensing: the EM9305
component remains `source_complete=false`, stock-retained, and blocked by the
unresolved binary authority above.

The separate EM9305 record-package receipt proves that the four-record stock
container can be parsed, validated, and rebuilt byte-for-byte by maintained MIT
software. It deliberately records `source_image_complete=false` and
`production_routed=false`: deterministic packaging neither supplies the four
record sources nor resolves controller redistribution authority.

The executable gate accepts an `authorized` component only when a grant/license
artifact and a separate compliance record are independently stored below that
component's `docs/release-authority/` directory, are distinct regular files,
and match their recorded SHA-256 values. A status edit, a shared file used for
both roles, a link, or mutable-path evidence cannot open the gate.

## What may be published now

Only the deterministic source ZIP produced and verified by
`tools/community_distribution.py`, or a separately created clean history made
from that verified ZIP and audited across its entire reachable object set, is
within the project's current public-release boundary. The existing full Git
history is not safe to publish or mirror: it contains tracked `g2/.tmp-*`
donor/build artifacts. Current ignore rules prevent new local temp and hydration
state from being added accidentally, but they do not sanitize prior commits or
objects. Do not substitute `git archive`, a hosting provider's automatic source
archive, or a mirror of this history for the verified source ZIP.

The ZIP is a source archive for a hybrid source-overlay build, not a firmware
binary release. It includes the mixed-license Touch candidate evidence in
`tools/manifests/g2-touch-final-source-candidate-provenance.tsv`: six
semantic-only rows, all with `production_elf_ownership=false`. It contains no
official payload or retained stock byte and does not make the candidate stock
addresses publicly redistributable.

Local hydration deliberately writes the six authenticated official payloads
and `.open-cfw-local-hydration.json` into the recipient's extracted workspace.
That hydrated workspace and every binary built from it are outside the
official-payload-free source statement. Public binary redistribution remains
unauthorized by this project until durable authority is recorded for all six
payloads. Hardware qualification is separately blocked by unavailable physical evidence;
source verification and software-only build results are not device-validation
evidence.

The verified source ZIP carries the authenticated root `.gitignore`. In a
fresh extracted Git tree it excludes the six local provider paths, hydration
receipt, build output, nested temporary state, and canonical lock files while
leaving source, provenance, and community-policy documents addable. This
reduces accidental staging risk after hydration; it does not make a hydrated
tree or stock-bearing build output redistributable.

## Compiled source inventory

At the time of this audit, the two overlays, including the PT post-link
provider's exact source/header records, form an inventory reference 786 unique,
content-addressed source files. The live audit
derives overlay records from `sources`, `isolated_leaves`,
`in_place_leaves`, and `relocated_leaves`, checks each file hash, checks the
declared license identifier, authenticates the exact mapped license-text bytes,
rejects conflicting duplicate identity/license metadata, and independently
enforces the authenticated 459-row project-owned MIT census.

| Declared license | Unique files |
|---|---:|
| MIT | 574 |
| Apache-2.0 | 81 |
| BSD-3-Clause | 101 |
| Zlib | 27 |
| BSD-2-Clause | 2 |
| GPL-3.0-only | 1 |

All current compiled-overlay source records are license-metadata clean. The overlay inventory
contains 574 MIT records in total. Of the 460 exact project-owned policy rows,
459 remain compiled and one (`imu_icm45608.c`) is retained only as MIT-licensed
repository research. The production image now keeps the authenticated stock IMU
donor object instead of compiling that wrapper or its TDK dependency closure.
The sole GPL source is the authenticated g2flash `ring_gesture.c`. InvenSense
EDMP headers carrying dense payload bytes or an express-license-only
redistribution notice are not treated as ordinary BSD source merely because a
root license file exists; none enters the public bundle, which also denies all
fifteen known risk paths by exact identity. Shared littlefs, EasyLogger, and
other provider records retain their authenticated upstream terms.

The separately audited repository-wide public-and-research license closure
contains 894 distinct project-authored MIT-compatible files. Of these, 890
G2-internal files carry an inline SPDX expression permitting MIT. The four
root community policies (`CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`,
and `SUPPORT.md`) inherit MIT under the exact authenticated root `LICENSE`;
their names, sizes, individual SHA-256 identities, and aggregate census digest
are fail-closed inputs to the same audit. Its newly
distributed controller/build
adapter tranche is exhaustive over 107 C, header, assembly, and Python files:
104 project-authored paths with an SPDX MIT option and three Touch CAT2/Cortex-M
adaptations that correctly remain Apache-2.0. This community census does not
change the 786-file compiled overlay inventory above.
It also includes the six-file open Touch source-image package, its MIT proof
analyzer, and two focused MIT tests; these remain software-only source
artifacts and do not alter the official Touch payload or its redistribution
authority.
The G2-internal census also covers the four project-authored MIT community
archive entrypoints (`g2/community/Makefile`, `g2/community/make.sh`,
`g2/docs/community-archive-README.md`, and
`g2/tests/test_community_markdown_link_closure.py`).
The closure also includes the 28-file MIT PT-protocol C/header source set;
provider adapters and production routing remain explicit, separate gates.
In addition to these repository-wide censuses, the community bundle constructs
a deterministic member-level ledger. Code-like members must carry a recognized
SPDX marker or match one narrowly reviewed upstream scope whose exact license
artifact is included and authenticated. Explicit ownership/provenance classes
cover project documents and data, generated receipts, upstream provenance, and
license evidence, so every selected payload member is classified. The generated
`BUNDLE-MANIFEST.json` envelope is project-authored MIT material under the
included root `LICENSE`; it is necessarily outside its self-authenticating
payload ledger. The verifier recomputes that ledger from the immutable ZIP
bytes; an unclassified or restrictively licensed payload member cannot be
hidden behind aggregate counts. Each included license text has an exact
independent SHA-256 pin, and the member census rejects omitted, unused, or
unrecognized alternate terms. The two CMSIS-FreeRTOS queue adapters point to
the included Arm Apache-2.0 license rather than another component's Apache
notice.

The exact live inventory, including SHA-256, license, upstream reference,
and component, is available without network access:

```sh
cd g2
python3 tools/audit_g2_release_licensing.py --json
```

Run `make release-license-audit` for the informational audit. Run
`make release-license-gate` to exercise the intentionally failing public-release
gate. Closing the gate requires durable redistribution authority for every
binary payload and resolution of every source-license metadata error; adding
source code, a decompiler finding, or a checksum is not sufficient.
