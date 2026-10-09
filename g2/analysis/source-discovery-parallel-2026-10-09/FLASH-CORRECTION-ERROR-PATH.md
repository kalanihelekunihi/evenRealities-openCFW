# Correction and bounded mode-predicate error path

The previous FLASH-VERSION-BOUND-COMPARISON.md is preserved as a raw historical report. Its claimed stock/sample four-byte-mask discrepancy is **withdrawn**. Independent evidence: ../coverage-audit-parallel-2026-10-09/FLASH-INDEPENDENT-REVIEW.md (hash in new receipt). Official DEF.h119 defines FLASH_4BYTE_CF_MASK0x20; CMD.c97–113 uses it for RDCR15. DEF.h121's0x40 belongs to the alternate RDSCUR2B branch CMD.c115–122. Stock4703DC requestsRDCR15 and470434 tests bit5, so both agree. The earlier final/commentary mismatch statement must not be reused. No register-layout/part discrepancy remains from that claim.

## Actual static issue

Authenticated2.2.6.10 OTA SHA36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863:

1. Generic read470168 calls HAL4C2098 at4701F0, saves its return inr4 at4701F4, logs on nonzero, and returnsr4 at47020C. Its null/invalid inputs also return nonzero2/6/5 before HAL.
2. Predicate4703C6 requestsRDCR15 into stack+8.4703E2 saves generic read status inr4;4703E4–E6 tests it. A nonzero status follows logging and47042C returnsr4 unchanged. Only status zero reaches470430 and the bit5 test. Thus return domain combines booleanfalse0, booleantrue1 and nonzero error statuses.
3. After successfulB7, caller4705BC waits and4705C0 invokes predicate.4705C4 compares its return to0;4705C6 branches to470610 on **any nonzero value**, including a propagated read error. Zero takes the rejection path.470610 performs the next call4706E0, whose result remains checked.

Bounded conclusion: this callsite cannot distinguish readback true from nonzero readback errors. A transport error can select the same proceed branch as mode-set true; this does not establish final initialization success, physical flash failure, observed runtime reachability, or any actual hardware event. Later checks may still fail. B7 command errors themselves are handled separately at470570–572 and do not use this predicate shortcut.

The vendor sample IsFlash4Byte returns a boolean from the appropriate register bit; it is a protocol comparator, not the producing Apollo driver source or a justification to erase stock error behavior. A future reconstruction must preserve the observed mixed return/proceed behavior unless an explicitly authorized behavior change is intended. No proprietary sample/firmware execution, emulator/device/canonical/index changes were performed.
