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

## Compiled source inventory

At the time of this audit, the two overlays reference 757 unique,
content-addressed source
files. The live audit derives every record from `sources`, `isolated_leaves`,
`in_place_leaves`, and `relocated_leaves`, checks each file hash, checks the
declared license identifier, and requires an available license text.

| Declared license | Unique files |
|---|---:|
| MIT | 545 |
| Apache-2.0 | 80 |
| BSD-3-Clause | 95 |
| Zlib | 27 |
| ISC | 7 |
| BSD-2-Clause | 2 |
| GPL-3.0-only | 1 |

All current compiled-overlay source records are license-metadata clean. The overlay inventory
contains 545 MIT records in total; 460 are the exact project-owned targets in
the normalization census, while the remainder retain applicable upstream MIT
provenance. The sole GPL source is the authenticated g2flash `ring_gesture.c`.
File-specific upstream terms control the pristine InvenSense ICM45608
implementation files. InvenSense EDMP headers carrying dense payload bytes or
an express-license-only redistribution notice are not treated as ordinary BSD
source merely because a root license file exists; the public bundle fails
closed while any such file remains in its transitive source closure. Shared littlefs, EasyLogger, and
other provider records retain their authenticated upstream terms.

The separately audited community-source license closure contains 884 distinct
project-authored MIT-compatible files. Its newly distributed controller/build
adapter tranche is exhaustive over 107 C, header, assembly, and Python files:
104 project-authored paths with an SPDX MIT option and three Touch CAT2/Cortex-M
adaptations that correctly remain Apache-2.0. This community census does not
change the 757-file compiled overlay inventory above.
It also includes the six-file open Touch source-image package, its MIT proof
analyzer, and two focused MIT tests; these remain software-only source
artifacts and do not alter the official Touch payload or its redistribution
authority.
The closure also includes the 28-file MIT PT-protocol C/header source set;
provider adapters and production routing remain explicit, separate gates.
In addition to these repository-wide censuses, the community bundle constructs
a deterministic member-level ledger. Every selected source-like member must
carry a recognized SPDX marker or match one narrowly reviewed upstream scope
whose exact license artifact is included and authenticated. The verifier
recomputes that ledger from the immutable ZIP bytes; an unclassified or
restrictively licensed member cannot be hidden behind aggregate counts.

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
