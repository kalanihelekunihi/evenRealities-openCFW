# TDK stock-binding: finite discriminator search

## Result

**No stock revision attribution to TDK 1.1.2 or 1.1.8 is established.** A byte-bound nine-element host transform is newly explained and excluded as the official int8 mounting wrapper. No address-bound unequal-ODR calibration-key write to sensor SRAM 0x50 was recovered in the inspected scope. This is a bounded negative attribution result, not proof that either operation is absent from the whole firmware.

## Authenticated coordinates

Locked bundle SHA-256: `f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`.
Canonical Apollo main flash starts at `0x438000`, length 3,523,364, SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`. Its bytes were freshly checked equal to official `ota_s200_firmware_ota.bin[32:]`; payload SHA is captured in source-guided-constants-and-callers.json. This agrees with the canonical fixed-image integrity receipt.

The function-symbol census consulted 8,844 in-image rows; 8,818 nonempty extent hashes verified with no mismatch. Hashless rows are not treated as byte-bound matches. Thumb/LE Capstone decoding and symbol extents are search aids, not whole-image code classification proof.

Official discriminator source is pinned by `../source-discovery-parallel-2026-10-09/TDK-EDMP-REVISION-COMPARISON.md` and its revision receipt: 1.1.2 `b79ae575f7f310e5ae2e1164096d1a858bb74662`, 1.1.8 `edaf335913c9ede7d4b5d8700e49b279cfb8fa8b`. New inv_imu_edmp.c SHA is `30a7b0541b33a7e1796324b279b36a41dab89ce95d5e9bbce2bb0f0086f2a19c`.

## Nine-entry Q14 candidate

`0x4A460C–0x4A46B0` (164 bytes), SHA-256 `eb7fb1b0a03d0c5ee0cf2ec5d2925c82be8399d93bdd7f7fc50ecfcbbd1cc00f`, is historically labeled semantic_set_orientation_matrix. Original instructions show float32 input through r2, nine iterations, Q14 fixed conversion at `0x4A465E`, and halfword cache stores to `0x20000E00`. Raw float words are copied to `0x20000E38`. Q30 values go to `0x20000E14`, with negation for columns 0/1 and positive column 2. No calls occur in the function.

The directly bound caller is HUB_IMUCalibParaInit `0x4A6BCE–0x4A6D26`, SHA `6f299b00e6a3da2ca6a18610cc14db268c22f9710a70490d2c78bc42420d8237`, callsite `0x4A6C02`, passing its stack matrix at sp+0x68. See retained original disassemblies and orientation-pseudocode.txt. This explains a host calibration transform useful for interpreting axis conventions. It does not bind the official int8→int16 mounting conversion or sensor SRAM write at 0x1AC (18 bytes).

The broad verified-range LSL #14 scan retained 14 candidate ranges. None contains an LDRSB; only the Ins_SxyTCA candidate contains halfword stores, with a different set of object offsets rather than a nine-entry mounting array. Float conversion is handled separately above. This query cannot exclude packed loads, multiplication, vectorized or optimized constant matrices.

## Unequal-ODR calibration-key discriminator

Official 1.1.8 tests unequal accel/gyro periods, copies four bytes at calibration-image offset zero and writes size four to sensor SRAM 0x50. The acquired calibration array is 189 bytes, SHA `517966d94b8304b85baf284c5de87c12c00af7debb72d73e99a9acc744dfc8e0`; header SHA `26ca324dd54854d98cfd1d9fb3bc32c0b99251f1a1ba6b2ab61a9a3d67d225d9`. Exact searches for full image, 32-byte prefix, 16-byte prefix and four-byte key `f1 70 0c 78` each returned zero main-flash matches.

A verified-range call heuristic (MOV r1,#0x50 plus MOV r2,#4 and BL/BLX in preceding 8/following 11 instructions) returned zero candidates. A relaxed MOV r1,#0x50 search retained 20 ambiguous contexts, with zero direct MOV r1,#0x1AC hits. The IMU-region context at `0x4A5ABA` lies in DRV_IMUDataParserCallback `0x4A56D4–0x4A5B66`, SHA `5fab36a38d5542001f2b3a96ce9cbba2f00aa3dcb01c49f62280e84244f0c03e`. It sets r2=0 and calls 0x43C0E4 on r8; the same nearby call uses r1=12/r2=0. It is not evidence of the desired four-byte SRAM write. No callee ownership attribution is inferred from an unverified short symbol extent. All relaxed contexts are retained, not silently accepted or discarded.

## Exact boundary and next evidence

To discriminate revisions, we need an authenticated address/callgraph binding for the actual inv_imu_write_sram-compatible host transport and GAF configuration routine, or an authenticated occurrence of the calibration image in initialized/decompressed memory with provenance to the locked payload. Then trace the unequal-period comparison and the 0x50/four-byte write, and separately inspect any int8 nine-element conversion and 0x1AC/18-byte write. Missing exact prefixes in raw main flash and absent helper labels do not select 1.1.2: changed blobs, compressed initialization, indirect transport and compiler folding remain possible. This batch claims neither private EDMP ROM knowledge nor sensor algorithm equivalence.

Validation is static original-byte/hash/disassembly and source-guided search only; no original-instruction execution test was performed for this TDK batch. Prior audio tests were not rerun for this result. Shared seals, 110 inputs, four checkpoints and observed index are checked in preservation.json. No Git mutations, production edits, devices, registry or canonical ledger changes.
