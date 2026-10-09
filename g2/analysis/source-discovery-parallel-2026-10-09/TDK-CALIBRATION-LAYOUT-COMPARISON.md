# Stock TDK calibration patch and EDMP layout

The authenticated stock calibration image at `0x6D53D8` exactly matches all **125 bytes** of official ICM45608 Release 1.1.2, commit `b79ae575f7f310e5ae2e1164096d1a858bb74662`. Both hashes are `80eb396ba1b365d332aabebed514cccb19f5d5a8eba1d6543be61ceda4fa8b2f`. Fresh comparison used locked 2.2.6.10 payload bytes; raw image SHA256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`. This is complete patch-byte correspondence, not a prefix match or whole-driver source proof.

Matching old headers were extracted with git show from already acquired official history into `tdk-1.1.2-calibration-reference`; no network acquisition, submodule/index change or downloaded code execution was needed. Upstream https://github.com/tdk-invn-oss/motion.arduino.ICM45608 ; root BSD-3-Clause and individual notices retained. Per-file source hashes are in that directory's provenance.json.

| Contract | Stock address-bound audit | Official 1.1.2 | Official 1.1.8 |
|---|---|---|---|
| Calibration image | 125 bytes at6D53D8 | Exact125-byte match |189 bytes, different hash517966d94b8304b85baf284c5de87c12c00af7debb72d73e99a9acc744dfc8e0 |
| RAM program base |5072A2 suppliesC80 |inv_imu_edmp_defs.h51:C80 |defs.h50:C5C |
| Acceptance key offset |5072B0 copiespatch+8 |patch_key_offsets.h41:8 |offsetC |
| Acceptance patch point |5072C2 suppliesB4 |patches_defs.h59:B4 |B4 shared |
| Mounting matrix |507710 passes18bytes to1AC |memmap.h97–98:1AC,size18 |Same1AC,size18 |
| Unequal-ODR extra patch |No extra50 write at bound insertion point |No added branch in compared hostC |Conditional keyoffset0 ->SRAM50 |

Stock's acceptance key bytes are `f1700cc0`, the exact old patch bytes at offset8. Mounting correspondence is a shared map contract: stock consumes an existing18-byte Q14 cache directly; this does not prove presence of the public nine-int8 conversion wrapper. Transport7C/7E protocol correspondence remains separate from patch identity; the audit records callback ABI differences, so exact public host-driver source identity must not be assumed.

## Finite public history discriminator

The existing official repository history identifies calibration changes at Release1.0.7 commit `10c7c929599d7c31a91eea001395a0d0c856588a` and Release1.1.3 commit `75fb1214413915d29cd9e4eeae4f263a3bbfdb19`. Extracted header bytes show1.0.7 already has the exact125-byte stock patch;1.1.3 has the189-byte image whose hash matches1.1.8. Therefore patch identity admits multiple historical revisions and selects an **older patch lineage**, not a unique producing release. A mixed/private vendor integration could also retain old patch bytes with other host changes.

The partial match materially resolves the old calibration-header gap and corroborates C80/+8/B4 setup. Producing revision/compiler/configuration, complete host source, other patch images/maps and private EDMP/GAF ROM computation remain unproven. No sensor execution, physical behavior, firmware reconstruction completeness or bundle equality follows.

See `TDK-CALIBRATION-LAYOUT-RECEIPT.json` for exact stock/history byte hashes and `../coverage-audit-parallel-2026-10-09/TDK-TRANSPORT-CALLGRAPH-REPORT.md` for bound original instruction edges. Canonical owner may reuse existing registered TDK provider; this evidence does not justify changing its pin to1.1.8.
