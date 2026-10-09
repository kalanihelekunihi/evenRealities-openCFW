# Independent TDK stock-binding review

[Owner report](../tdk-stock-binding-search-2026-10-09/REPORT.md) is appropriately bounded: no stock SDK revision attribution is established. [Independent verification](TDK-STOCK-BINDING-INDEPENDENT-VERIFICATION.json) passes15 checks: canonical hash and OTA[32:] equality,8844 in-image symbol rows,8818 nonempty extent hashes with zero mismatches, candidate/caller hashes, acquired calibration header/189-byte array hashes, four independent raw-main prefix searches, and retained candidate counts. [Fresh independent GNU disassembly](TDK-ORIENTATION-INDEPENDENT-DISASSEMBLY.txt) confirms the selected transform without using the owner's decoder.

## Candidate accepted as excluded comparator

4A460C–4A46B0 authenticates at SHA eb7fb1b0a03d0c5ee0cf2ec5d2925c82be8399d93bdd7f7fc50ecfcbbd1cc00f. It loads float32 elements through r2, copies raw words, converts with original fixed-point VCVT instructions at fractional widths14 and30, stores Q14 halfwords, negates columns0/1 for Q30, and iterates nine entries. There is no BL/BLX or SRAM transport call in the selected extent. The owner's pseudocode correctly preserves VCVT rather than substituting a C cast. This is not the acquired TDK int8 mounting wrapper, which converts nine signed bytes and calls the SRAM-writing Q14 helper. It could still participate upstream in a larger host path; exclusion as the exact wrapper is not exclusion of all shared axis conventions or later consumers.

## Negative search boundaries

Exact full189-byte image,32/16-byte prefixes and four-byte key f1700c78 have no matches in canonical main flash. Independently reproduced. This says nothing about companion images, decompression/initialization, transformed data, changed patch revisions or algorithm absence.

The14 retained shift ranges and20 relaxed r1=0x50 contexts exist and their containing byte extents authenticate. The advertised call heuristic is explicitly a near-window pattern for specific registers and decoded MOV/BL forms, not complete argument dataflow. Its zero-result output was reviewed, not independently rerun: no reproducible query script is retained in the owner deliverables, and the local default Python lacks Capstone. Thus accept the reported finite heuristic result with that verification limit; do not elevate it to exhaustive code absence. Eight preceding/eleven following instructions cannot cover distant setup, literal loads, indirect calls, inlining, alternative ABI wrappers or tail branches. Likewise no LDRSB among LSL14 hits cannot exclude packed-load or constant-matrix lowering.

## Next binding assessment

No new source acquisition is justified by these negatives alone. A specific available static next step remains potentially useful: identify the stock sensor SRAM transport by its public register-access sequence and authenticated callers, then inspect the actual GAF setup path for unequal accel/gyro periods and four-byte0x50 writes. This requires a byte-bound transport candidate; merely re-running0x50/MOV or exact-prefix queries adds no new coverage. Separately, trace consumers of the proven Q14 cache0x20000E00 if an authenticated sensor-write caller emerges; the cache transform alone does not bind the18-byte0x1AC mounting write. Neither negative pass selects1.1.2 over1.1.8 or proves private EDMP ROM semantics.

No original firmware executed, no sealed test repeated, no canonical/index/source/device/Git changes. Full firmware/source/byte-equality exhaustion remains unproven.
