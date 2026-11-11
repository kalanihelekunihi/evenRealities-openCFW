# R1 static ST25 mailbox-mode update in C

`st25/native_mailbox.c` implements stock entry `0x5d1f4` with existing I2C5 read/write and delay providers. It reads one byte from address `0xae`, register `0x0d`; a nonzero read result returns immediately without delay or write. Success replaces bit zero with the low input bit, preserves bits 1–7, waits five milliseconds and returns the full write status. The static mailbox-mode register is separate from dynamic EH enable. No assembly or retained stock executable code is introduced.

REA binds the 78-byte update/write-helper window to the locked application. The write helper's delay at `0x78510` uses 64000 subtract-three iterations per millisecond, matching the existing C delay provider contract (`0x784f0` uses an identical primitive at a different address). Electrical timing remains unverified.

The C temporary byte is initialized to zero. Normal successful reads overwrite it. If a malformed backend reports success without writing output, the C fallback is deterministic; stock instead consumes the low byte of incoming R3 saved by its push instruction. This deliberate behavior improvement is tested separately, not claimed as stock equivalence.

Verification passes 27648 stock/C comparisons over every register byte, low/full-word enable inputs, read/write error words and poisoned stacks, plus 54 no-output fallback/error cases. Five compiled defects are rejected: wrong mask, wrong address, writing after read failure, missing delay and wrong enable bit. The normal probe passes after mutation testing. Full configuration integration now executes the mailbox C body and passes the existing 1440 direct pairs, 36 escaped-byte log-mutation pairs and 16 actual ST25 SDK-provider pairs; I2C/delay leaves and BSP registration remain modeled.

The normal open-toolchain build compiles 813 units (731 application, 82 bootloader), with 71 application imports and no new failures or duplicate strong symbols. The mailbox import closes with none added. All 812 previous source inputs are unchanged, and 810 previous object hashes are identical; two generated boot objects differ with output paths. No G2 source or source-qualification selection is changed. This is relocatable composition, not a finally linked application or device-boot claim.

Reproduction scripts and input hashes are recorded in [st25-mailbox-c-review.json](st25-mailbox-c-review.json).
