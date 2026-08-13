# Cordio DM connection-manager source recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The stock `dm_conn.c` closure contains 57 linked functions / 6,216 code
bytes. Fifty-six functions map to the Packetcraft r20.05 source inventory and
one adjacent 62-byte helper is a product/vendor addition with no public
definition. The code and interstitial-data interval is
`[0x004B5B24,0x004B7426)`; its separate trailing literal pool is
`[0x004B7426,0x004B7478)`. The complete 6,484-byte physical envelope has
SHA-256
`0fa4bda2fd946ce20605f08b8f824a9818367e29eb9df709f3393f2e8952d77f`.

Five public r20.05c APIs have no stock body, caller, or registered pointer and
are classified source-only/dead-stripped: `DmReadRemoteVerInfo`,
`DmExtConnSetScanInterval`, `DmExtConnSetConnSpec`,
`DmWriteAuthPayloadTimeout`, and `DmConnRequestPeerSca`.

This is an identification result, not a production replacement. All 6,484
flash bytes and the associated SRAM remain stock-retained.

## Source lineage

The selected public oracle is Packetcraft r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`, file blob
`746a7c107ac779a296552056c27488d3f94acd21`, 53,967 bytes, SHA-256
`4bc0ba3452eeab625a763f0597fe6e85e4b0c12c3c47c8368af412cc88480a69`.
The blob is unchanged from r20.05 through r20.05c and is Apache-2.0.

Stock is not a pristine copy of that file. It combines:

- the r20 separated connection-update component, `DM_ID_CONN_UPD` action and
  message dispatch, 36-byte message allocations, feature-event clearing, and
  peer-SCA action support;
- AmbiqSuite R2.5.1's suppression of the
  `DmConnIdByHandle not found` warning; and
- product validation/logger additions in `dmConnUpdExecute`,
  `DmConnPeerRpa`, and `DmConnLocalRpa`, plus the vendor helper.

The strongest classification is therefore “Packetcraft r20.05-family
architecture, rebased Ambiq/product patch stack.” The public file is the safe
per-function implementation oracle; it is not an exact whole-object or
whole-tree identity claim. Exact source/blob identities are pinned in
`tools/manifests/packetcraft-cordio-dm-conn-provenance.tsv`.

## Binary closure

The 57 exact half-open function intervals, SHA-256 hashes, r20 source spans,
direct caller counts, registered-table ingress, and classification are in
`tools/manifests/packetcraft-cordio-dm-conn-function-map.tsv`. The
concatenated function-body SHA-256 is
`0d23d0e293c47d791d1022ed70fd70795f6e1329b46740c10e6dd39f9c188e5a`.
The enclosing code/data interval contains 186 bytes of literal/alignment data;
the trailing pool contributes another 82 bytes.

Ingress is closed over 209 direct Thumb `BL` sites and thirteen intentional
aligned Thumb pointers. The registered tables are:

- main six-entry state action table at `0x00776A84`;
- update action and event map at `0x0078EFEC` / `0x0078EFF0`;
- main, secondary, and update component interfaces at `0x0078A820`,
  `0x0078A82C`, and `0x0078A838`; and
- connection defaults at `0x0078A814`.

No unexpected entry/interior pointer or exterior interior branch survives the
audit. One unaligned byte sequence at `0x006448D7` happens to decode as
`0x004B6C00`, but the aligned surrounding table word is `0x00004B6C`; it is
recorded and rejected as nonpointer data. A separate 606-byte function at
`0x005D2BAE` was also rejected: it is product math that merely references the
same source-path address, not `dm_conn.c`.

The retained source path is at `0x006DFFB4`, with exactly three pointer cells
at `0x004B652C`, `0x004B67E8`, and `0x004B7460`.

## ABI and SRAM

Stock proves `DM_CONN_MAX=3`, `DM_CLIENT_ID_MAX=5`, and `DM_NUM_PHYS=2`.
`dmConnCb` begins at `0x200712A4` and spans `0xC4` bytes:

```text
+0x00 ccb[3]          3 x 0x30-byte connection control blocks
+0x90 callback[5]     five client callback pointers
+0xA4 connSpec[2]     two PHY-specific connection specifications
+0xBC scanInterval
+0xC0 scanWindow
```

The main and update action-set pointer cells are at `0x20073FE4` and
`0x20073FD8`; the wider shared DM control block is at `0x20073B78`.
Public-facing connection messages allocate `0x24` bytes, one of the direct
r20 architecture discriminators.

## Lorelei handoff

The repository preserves
`research/readiness/dm-conn/`, 7,155 bytes, SHA-256
`84349c38b7fd59a1443cd5f3b324d4106016d946805175d81b18cda9dc9529bd`.
Its fourteen inner hashes authenticate the 61-function public source
inventory, nine conservative stock anchors / 3,652 bytes, two ARM GCC
profiles, thirty provider seams, and two non-vacuous links with zero unresolved
symbols. The corrected v2 package supersedes an initial 6,971-byte return;
the build and closure ledgers are byte-identical, while three line-drifted
anchor names/sizes are corrected.

Local analysis expands those conservative remote anchors to the complete 57
linked functions / 6,216 bytes. Reproduce both layers from `openCFW`:

```sh
python3 tools/analyze_g2_cordio_dm_conn.py --json
python3 tools/verify_research_corpus.py --json
```

Production promotion remains blocked on exact vendor diagnostics, IAR code
generation, placement, all provider relocations, and replacement tests. The
adjacent `dm_conn_sm.c` and `dm_dev.c` tranches are now independently closed;
continue with `dm_dev_priv.c` and then `dm_main.c` to resolve the privacy-event
consumer and global component-dispatch ownership.
