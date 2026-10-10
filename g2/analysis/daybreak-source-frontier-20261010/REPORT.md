# G2 newly accessible dependency-source frontier — 2026-10-10

**Independent-review correction:** The subsequent [EM9305 v4.2 comparison](../em9305-v42-reloc-independent-20261010-daybreak-low/REPORT.md) reproduced 40 exact **named symbol bodies/objects**, not 40 confirmed executable functions. Four are configuration/data-shaped. It also found `scan15_4CheckParameters` in the authenticated v4.6 SYM at a different size, so that item is a size discriminator, not absent by name. The original `receipt.json` is retained as the initial-pass record; use the independent `results.json` for corrected classifications.

This bounded pass reopened the completed fourth shortcut frontier only for public inputs that were not in its registered corpus. It found one useful historical EM9305 input, authenticated it at an immutable Git commit, and compared it directly with the locked G2 EM9305 payload. It did not change `.gitmodules`, any gitlink, the canonical coverage ledger, firmware source, or the `P2_EXECUTING` gate.

## Newly useful input

GitHub repository `C0R3YY2/em9305_original` exposes an EM9305 SDK tree at commit `e4412bc98d4e76d441d1226ca3696e53cfae5f54`. GitHub reports that commit as cryptographically verified, with tree `f5cb9ba00df71c2612d6d64cf39e05615a2feb64`. The repository contains a previously unavailable `emcore/bin/v4.2/standard` package: Intel HEX images, full symbol/size maps, and matching public headers.

Four files were fetched from commit-qualified raw URLs and independently hashed:

The verified files are retained locally under `third-party/local-vendor/sources/em9305-v4.2-public-mirror/` (an ignored vendor-input directory). The repository records their immutable identifiers and hashes in `receipt.json`; the downloaded bytes remain available for local follow-up without adding unlicensed mirror content to the tracked tree.

| File | Git blob | SHA-256 |
| --- | --- | --- |
| `emcore_standard.ihex` | `6bcbd1c3a417c676ce611de4b2d1cab00004562a` | `0e9d2e7ef4d2572a7fcdf5ae76e99c806b657b7b00740b86fb696c0b2bdf5b95` |
| `emcore_standard.sym` | `7955274387f9d7a85708b8e18f06a977b42c168e` | `c27c8dce8445e13845c9c1d9f32db76ca30f0cffc4ceeadb0a85cf8979775828` |
| `includes/qf_port.h` | `eaefb5c29a08b59510153900668d0ea883193f23` | `38eb135fc6beac9d44fec514901b369c74b89fda1b44f14baa1600ecc213a065` |
| `includes/hw_versions.h` | `91043a0c1b5200667b3bcf93b976a406748d4976` | `c865fbbbcdd7b81edcb1ec2c560b85a3addbc65107b9223f94afdceb7ca1bba5` |

The `qf_port.h` SHA-256 is identical to the already authenticated SDK v4.6 copy, so that header alone is not a version discriminator. The v4.2 image and symbol map are the useful new evidence.

## Direct stock comparison

The v4.2 Intel HEX parsed to 33,434 addressed bytes. The symbol map supplied 302 complete functions of at least 24 bytes. Exact raw-body comparison against locked `g2/blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin` found 40 named v4.2 functions, each at one stock offset.

Eighteen of those matches discriminate v4.2 from the registered v4.6 standard image: 17 same-named v4.6 functions have different bytes, and `scan15_4CheckParameters` is absent by name from the v4.6 symbol map. The discriminating exact v4.2 providers are:

`IRQ_Cleaning`, `NVMEntry_CopyJLITable`, `NVM_AfterOperation`, `NVM_BeforeOperation`, `PML_Dbm2PmlRfPower`, `ProtTimer_StoreConfig`, `RF_BleChannel2RfChannel`, `RF_GetOutputPower`, `RF_Ln`, `RF_RfChannel2BleChannel`, `RF_SetMacTiming`, `RF_TestModeStart`, `SleepTimer_SetWakeupTime`, `VoltMon_UpdateFlags`, `gIRQ_PRIORITY`, `llPrbs9Payload`, `receiverTestCheckParameters`, and `scan15_4CheckParameters`.

This is stronger than the prior generic EM9305 v4.6 archive attribution: it binds 18 stock bodies specifically to the historical v4.2 standard image rather than merely to a shared SDK family. The remaining 22 exact bodies are unchanged in v4.6 and therefore identify provider lineage without selecting a release.

The result remains private P2 evidence. An exact body plus symbol map supports provider identity and release discrimination; it does not establish that the whole G2 EM9305 image was linked from the public standard image, prove the producing MetaWare project/options, or add accepted pseudocode coverage.

## Source and submodule decision

No submodule was added. The repository is a 128 MB personal mirror with no repository-level license declaration, and much of it duplicates the already authenticated v4.6 SDK. Pinning the whole mirror would add unclear redistribution terms and a large generated/build tree. The immutable commit, verified commit/tree identity, Git blob IDs, content SHA-256 values, and the finite comparison receipt preserve the useful provenance without changing shared `.gitmodules`.

The historical `lvp_tws` GitLab route was also tested with noninteractive SSH and still rejected the available key. Current public NationalChip GitHub inventory contains no `lvp_tws` repository. No new NationalChip producing source was authenticated.

## Boundary

This finding reopens only the EM9305 version-discrimination branch. It does not reopen implementation or later workflow gates. Remaining progress from this source is a scoped independent review/admission of the 18 version-discriminating bodies and, if needed, relocation-aware comparison of larger v4.2 routines. Producer-version MetaWare project inputs, source for proprietary EM9305 libraries, and hardware behavior remain unavailable evidence classes.

Machine-readable provenance, comparison counts, and the release-discriminator inventory are in `receipt.json`.
