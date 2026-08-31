# G2 core-source notices

SPDX-License-Identifier: MIT

The core-source package combines openCFW source, adapted upstream source, and
retained official firmware bytes. This notice covers the source portions only;
it does not license or assert redistribution authority for retained Even,
NationalChip, EM9305, touch-controller, charging-case, or stock ICM45608
firmware bytes.

Project-owned OpenCFW files are licensed under MIT; the repository text is
`../LICENSE`. The separately retained `ring_gesture.c` source remains under
its authenticated upstream GPL-3.0-only license, whose complete text is
`components/apollo_main/ring_gesture/LICENSE`.

Upstream-derived files retain their original notices and terms. Complete terms
used by the current production source graph are available at:

- Apache-2.0: `third_party/cordio/LICENSE.md`
- BSD-3-Clause: `third_party/littlefs/LICENSE.md` and
  `third_party/ambiqsuite-apollo510/LICENSE`; retained TLSF terms are in
  `components/apollo_main/core_overlay/tlsf.h`, and Ambiq ANCC terms are in
  `third_party/ambiqsuite-ancc-profile/ancc_main.c`
- BSD-2-Clause: `third_party/lz4/LICENSE`
- MIT: `third_party/freertos-kernel/LICENSE.md`,
  `third_party/easylogger/LICENSE`, `third_party/tinyframe/LICENSE`,
  `third_party/ring-buffer/LICENSE`, and the component-specific license copies
  under `components/apollo_main/core_overlay/`
- Zlib: `third_party/nanopb/LICENSE.txt`

The research-only InvenSense ICM45608 snapshot is not part of the production
source graph or community source bundle. Its root license does not override
five file-specific restricted notices; the restricted headers, dense EDMP
payload headers, research adapter, and research candidate are excluded from
public release input. The canonical profile instead retains the authenticated
stock 12,436-byte IMU object as an explicit donor boundary.

The complete content-addressed inventory and unresolved-authority statement are
in `docs/release-licensing-and-redistribution.md` and are enforced by
`tools/audit_g2_release_licensing.py`.
