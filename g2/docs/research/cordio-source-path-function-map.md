# Apollo Cordio source-path/function map

## Result

The authenticated Apollo-main image retains 36 unique Cordio translation-unit
paths. The audit-hardened 64-shard Ghidra replay associates 32 of those paths
with 114 distinct functions; four paths retain raw pointer cells but have no
function anchor in the decompiler corpus. This is a closed ownership-anchor
census, not source coverage and not an exact-tree attribution.

`tools/analyze_g2_cordio_source_map.py` composes two existing read-only
authorities:

- `tools/analyze_apollo_embedded_source_paths.py`, which authenticates the
  3,523,396-byte Apollo image (SHA-256
  `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
  and the 64-log/7,370-function Ghidra corpus (`SHA256SUMS` SHA-256
  `3ff8aa908e5841823df9384cfbffca91d657816274797f332a45ff93a8aa832f`);
- `tools/analyze_g2_cordio_version.py`, which pins the independent ATT and DM
  r20.05-or-later discriminators and the limited public r20.05--r20.05c
  source-equivalence interval.

The resulting normalized path/function map has SHA-256
`772063dc1841dc33523e68ecca9188923e28efd5cbe6db5a22a36979c41b2623`.
The analyzer fails closed if the image, corpus, 36/32/114 census, ownership
boundary counts, or normalized map changes.

## Evidence recorded per anchor

For each retained path the JSON report records its runtime string address,
all raw pointer cells, ownership-boundary classification, and every anchored
function's entry and inclusive Ghidra body bounds. Each function record also
contains mechanical direct-call topology, sub-`0x10000` literal constants,
and the fifth argument passed to the authenticated logger/assert provider
`FUN_0043d574` when that argument is an immediate source-line value.

Those line values include assertion, error, and trace sites; they must not be
described collectively as assertions. For example, the FreeRTOS-port
`wsf_buf.c` anchor at `0x00530446` contains line 321, agreeing with the
independently pinned `movw r0,#321` instruction in the version analyzer.
The `atts_csf.c` path has eight anchored functions and line values 128, 179,
200, 239, 246, 286, 291, 311, 370, 396, 422, and 444. The sole
`dm_conn_sm.c` anchor at `0x00533EF4` carries lines 141, 152, 154, 155, and
160. These are useful source-shape constraints, but local trace changes mean
they cannot authenticate exact public file text.

Run the report with:

```sh
python3 tools/verify_research_corpus.py \
  --extract /var/tmp/opencfw-research/corpus

python3 tools/analyze_g2_cordio_source_map.py \
  --ghidra-corpus /var/tmp/opencfw-research/corpus/apollo-main/ghidra.3LC1Dq/full64-j64-auth \
  --json
```

## Public-upstream boundary

The 36 paths divide into 22 generic Packetcraft stack candidates, five Ambiq
ports, and nine Ambiq/application or Even-product-layer files. The generic 22
remain candidates only: a path match does not prove pristine upstream source.

The following remain explicitly outside the pristine public Packetcraft
boundary:

- `ble-host/sources/hci/ambiq/hci_evt.c` and all four retained
  `wsf/sources/port/freertos` paths;
- all nine `ble-profiles/sources/apps/app` paths, including the Ambiq-layout
  `app_db.c` that contains Even MRAM/product persistence extensions;
- all other Even `platform/ble`, custom service/profile, policy, callback, and
  controller glue, whether or not it retained a Cordio-like interface.

Being outside the public Packetcraft boundary no longer means that the Ambiq
HCI event object is unbounded. The focused
[HCI event recovery](cordio-hci-evt-source-recovery.md) accounts for all 80
official Ambiq R4.4.1 source-family functions: 79 linked stock bodies and the
sole dead-stripped `hciEvtGetStats`. Its 85-entry parser and callback-size
tables, complete physical interval, direct-call closure, and stored-pointer
ingress are mechanically pinned. The proprietary source remains an oracle
only; no source bytes are redistributed.

The production-excluded r20.05c snapshot remains a source oracle only. No
production overlay or manifest was changed by this increment.

The nine application paths now have a narrower downstream oracle of their own:
the exact Apache-2.0 AmbiqSuite 2.5.1 source set at public import commit
`de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`. The authenticated path map
anchors 50 functions / 29,110 bytes, while the focused legacy master/slave
audit recovers 11 additional functions beyond the three path-anchored legacy
bodies. This closes their third-party ancestry without misclassifying G2's
ten-record MRAM, privacy, pairing, connection, diagnostic, and UI extensions
as upstream source. See
[the application-framework recovery](ambiqsuite-cordio-app-framework-source-recovery.md).

The subsequent [source-path recovery audit](apollo-embedded-source-path-recovery.md)
independently recovers four functions at `0x0052A474`, `0x0052A51A`,
`0x0052A542`, and `0x0052A574` from the baseline-unanchored `wsf_timer.c`
path using direct-call witnesses. The [focused timer audit](cordio-wsf-timer-source-recovery.md)
now closes their private timer ABI, lock providers, globals, and dispatcher
callers and adds an eleven-function clean-room behavioral candidate covering
the complete 536-byte code cluster. It remains
production-excluded. Official AmbiqSuite 2.5.1 now pins the exact proprietary
implementation/source family, but source redistribution is not permitted and
minor local text/config drift, exact compiler output, and final
placement/relocation qualification remain unresolved.

## Version claim and blockers

The authenticated public interval is r20.05, r20.05a, r20.05b, and r20.05c
only for `AttsCsfWriteFeatures`, the eight-event `dmConnSmExecute` shape, and
the individually audited blobs that are unchanged across those releases.
There is still no exact upstream commit claim for the complete G2 vendor tree.

Promotion of the remaining Ambiq and product-local objects is still blocked on
authenticated source/configuration evidence—especially for the FreeRTOS ports—
plus per-function ABI, boundary, exterior-reference, and relocation closure.
The completed `hci_evt.c` audit is the exception: its clean-room metadata is
closed, while its proprietary implementation remains intentionally excluded
from source reuse. Other unresolved candidates remain production-excluded and
their official ranges remain cut forward.
