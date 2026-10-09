# Official TDK EDMP host-driver revision comparison

Compared the existing registered ICM45608 revision `b79ae575f7f310e5ae2e1164096d1a858bb74662` (1.1.2) against isolated official acquisition `edaf335913c9ede7d4b5d8700e49b279cfb8fa8b` (1.1.8). Upstream: https://github.com/tdk-invn-oss/motion.arduino.ICM45608 . Root license BSD-3-Clause; retain individual source notices. The complete inv_imu_edmp.c diff contains only the changes below.

## Finite discriminators

1. New `inv_imu_edmp_set_gaf_parameters` lines 606–611 tests `acc_odr_us != gyr_odr_us`. On unequal periods it copies a patch key from calibration image offset **0x0** (`RAM_CALMAG_IMG_CHUNK0_PATCH_KEY_OFFSET`, patch-key header line 39), then writes that key to SRAM patch point **0x50** (`EDMP_INVN_ALGO_GAF_PATCH_POINT_CHUNK0`, patches header line 34). Both revisions preload the calibration image and unconditionally install the subsequent PART4 acceptance key. The added unequal-period branch and extra write are the strongest finite host-code discriminator here. They do not expose the algorithm implemented in sensor ROM.

2. Both mounting wrappers convert exactly nine int8 entries using `(int16_t)mounting_matrix[i] << 14`. Old code writes the resulting matrix directly through `INV_IMU_WRITE_EDMP_SRAM`; new code delegates to added `inv_imu_edmp_set_s16q14_mounting_matrix`, which performs the same write. A surviving helper/call boundary can distinguish source structure, but optimization may inline it. Missing helper structure in a stripped image does not establish the older revision. This comparison reports source operations, not behavior of every possible signed input under C-language rules.

3. Interrupt-vector configuration is unchanged. It writes three uint16 entries for EDMP ROM base, base+4 and base+8 as six bytes beginning at `EDMP_PRGRM_IRQ0_0`, then writes the stack-end high byte to `EDMP_SP_START_ADDR`. This cannot distinguish these two revisions. EDMP initialization/configuration services do not provide private ROM implementation source.

## Authenticated-firmware boundary

Consulted `g2/symbols/apollo_main.tsv` for EDMP, mounting, CALMAG, GAF and imu_icm labels; no records were returned. Exact configure/mounting/GAF function names were also absent from consulted `g2/workflow/tasks/*/contract.json`. These are bounded searches, not proof that routines are absent. Existing `docs/hardware/components/icm-45608.md` records the older TDK lineage and historical source locations; its statement that RAM images should match Apollo blobs is a hypothesis, not a verified occurrence. Historical overlay paths it cites are removed in this checkout.

No current address-bound authenticated-firmware record was found for the selected routines, so no stock revision attribution is claimed. The emulator's reported literal header scan was not reused as freshly verified evidence because its generated result was unavailable locally. A valid next comparison needs authenticated callsites/ranges: test for the unequal-ODR branch and write to patch point 0x50, inspect the nine-entry conversion/write path, and separately compare calibration image bytes. Vector agreement alone and absent exact blob matches cannot select a revision or establish ROM equivalence.

## Acquisition and owner proposal

Acquisition is isolated at `acquisitions/tdk-icm45608-emulator-lead`, detached at the pinned 1.1.8 commit. File hashes are in `tdk-edmp-revision-receipt.json`; the exact host-driver diff is in `tdk-edmp-1.1.2-to-1.1.8.diff`. Prefer the existing registered `third-party/upstream/invensense-icm45608` path. No new submodule is necessary; a revision update is only proposed for owner review after firmware attribution. No index, .gitmodules, firmware, seals, device, or canonical-ledger changes were made by this comparison, and downloaded code was not executed.
