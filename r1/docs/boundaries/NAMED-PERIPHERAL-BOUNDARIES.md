# Named temperature and power peripheral boundaries

## Policy

Recovered part names are sufficient to reject a default assumption of R1 authorship, but they do
not by themselves prove that a whole surrounding function is vendor source. This document records
the original attribution gates. The owner-authorized full-reduction policy of 2026-08-14 now
supersedes those gates for GXT310, QMA6100, and YHM2710. Each body stays
pinned by exact size and SHA-256.

## GXCAS GXT310 temperature sensors

The image names `GXT310X0` at I2C address `0x90` and `GXT310X2` at `0x94`, plus GXT310 mode-switch
and one-shot diagnostics. GXCAS documentation identifies GXT310 as a factory-calibrated 16-bit
I2C/SMBus temperature sensor optimized for body-temperature measurement. As of the 2026-08-11
source-admission review, [GXCAS's official download catalog](https://www.gxcas.com/download.html?page=17)
lists `GXT310-STM32 driver-V1.0` and links
[`GXT310_STM32驱动程序V1.0_202506_20251013111351.zip`](https://www.gxcas.com/uploads/files/202510/GXT310_STM32%E9%A9%B1%E5%8A%A8%E7%A8%8B%E5%BA%8FV1.0_202506_20251013111351.zip).
That listing is useful provider-discovery
evidence, but the archive endpoint timed out through both the direct and browser-backed retrieval
paths available to this workspace. Its bytes, license, API, and relationship to the older R1 image
therefore remain unauthenticated. No exact R1 driver source/version or redistributable provider
package has been admitted.

| Recovered entry | Size | Boundary evidence |
| --- | ---: | --- |
| `0x00050F9C` | 138 | enables the two named variants at `0x90` and `0x94` |
| `0x0006F804` | 8 | thunk into the `0x90` mode-switch path |
| `0x0006F818` | 98 | `0x90` one-shot path/body sharing |
| `0x0006F81E` | 8 | thunk into the `0x94` mode-switch path |
| `0x0006F832` | 6 | thunk into the `0x94` one-shot path |

These functions retain the attribution label `gxcas_gxt310_candidate`, but their five-entry
owner-authorized reduction is now compiled from `reconstructed/gxt310/`; see
[`GXT310-REDUCTION-CORRELATION.md`](../correlation/GXT310-REDUCTION-CORRELATION.md). The later
official archive remains documentation evidence only and is not a build input.

## YHMICROS YHM2710 power/charging controller

The image names YHM2710 initialization and system-track operations and verifies chip ID `0xA0`.
Public product information identifies YHM2710/2 as a programmable charging/current-monitoring and
shipping-mode family used in wearables. Exact driver source and licensing remain unresolved.

| Recovered entry | Size | Boundary evidence |
| --- | ---: | --- |
| `0x0003510C` | 224 | chip-ID check, initialization writes, and YHM2710 diagnostic |
| `0x000355BC` | 106 | YHM2710 system-track read/modify/write diagnostic |
| `0x0004E9E8` | 4 | exact thunk to `0x0003510C` |
| `0x0005079C` | 4 | exact thunk to `0x000355BC` |

These functions retain the attribution label `yhmicros_yhm2710_candidate`, but the complete
36-entry closure is now independently reconstructed as transparent C. Production enablement
requires Nordic board binding and owned-ring electrical validation, not an opaque provider.

The adjacent R1-owned three-client lease and NFC/`i2c_5` resource lifecycle are now split from
this provider and implemented without YHM register or wire operations. See
[`YHM2710-I2C5-RESOURCE-BOUNDARY.md`](YHM2710-I2C5-RESOURCE-BOUNDARY.md).
Exact mapping is in
[`YHM2710-REDUCTION-CORRELATION.md`](../correlation/YHM2710-REDUCTION-CORRELATION.md).

## Attribution re-examination 2026-08

GXT310: the official GXCAS STM32 demo archive now downloads (2,683-byte zip, SHA-256 pinned in
the report) but is license-free, structurally different from the R1 bodies, and postdates the
image — a documentation pointer only (address `0x90`, register `0x00`, ×0.0078125 LSB). QMA6100:
the pinned QST V1.0-lineage snapshot remains unlicensed, but
licensed public drivers now exist (RIOT `qma6100p`, LGPL-2.1; Espressif component, Apache-2.0)
that fully document the register map for any future datasheet-based rewrite; the R1 identity
adapter accepts chip IDs `0xFA` (QMA6100) or `0x9x` (QMA6100P). Both original gates were later
superseded by the owner-authorized reductions; the attribution findings remain valid.
Full evidence: [`withheld-providers-ATTRIBUTION-2026-08.md`](withheld-providers-ATTRIBUTION-2026-08.md).

## QMA6100 route decision 2026-08-14

The standing admission policy for QST QMA6100 requires both (a) official licensed source and
(b) established installed-part identity. Re-evaluated against the 2026-08 audit evidence:

- **Official source:** the only QST-authored code located is the pinned V1.0-lineage evaluation
  snapshot (`stephenshizl/code-learning @ 3903bd7d`, QST-author-identified `qma6100.cpp`), which
  carries no license grant. The licensed public drivers are third-party, datasheet-derived
  reimplementations (RIOT `qma6100p`, LGPL-2.1; Espressif component, Apache-2.0), not official
  QST source; additionally, RIOT's LGPL-2.1 is incompatible with static linking into this
  proprietary-blob-adjacent firmware image.
- **Installed-part identity:** not established. The stock probe order is LIS2DW12, then
  BMA456W, then QMA6100 as a fallback variant; both resolved variants are licensed and
  integrated, and no evidence shows a QMA6100-populated R1 ring.

Historical decision: the licensed-upstream route was declined. The later owner-authorized policy
instead reduced all three provider bodies plus fourteen coupled adapters to transparent C; see
[`QMA6100-REDUCTION-CORRELATION.md`](../correlation/QMA6100-REDUCTION-CORRELATION.md). Installed-part
identity is still required before Nordic startup selects that fallback, but no opaque QST element
is required by the compiled module.
