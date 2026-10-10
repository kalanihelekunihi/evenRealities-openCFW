# Independent FlashDB cache-count audit

PASS: four original-byte boundary cases independently replayed; two ARM layout probes match owner constants and object hashes; twenty receipt checks passed. Audit replay additionally asserts return PC100000 for every case (the original harness asserted SP/registers/results but omitted this explicit termination guard); all pass. Only audit-owned outputs changed. No storage/device/canonical admission/Git mutation.

## Accepted scope

Pinned header/source hashes are verified on replay. Sector getter543CC0..543CEC44bytes hash0d15a85efe5382c95472f445049055bc2bc4c863c55684c37857445b04581bcc and KV update543D1C..543E28268bytes hash401e21dae4030689d43d37aad6726150e094a8d5f2b263dac43d0b1d01b40932 authenticate against the locked header-bearing payload. The36c5 artifact hash is not the stripped raw-main hash; mapping correctly strips32bytes.

ARM32 unchanged header candidate:64/64 gives db2220, KVbase168, sectorbase680, node sizes8/24, addr offsets4/4, final user_data2216. Negative61/65 gives db2220 and sectorbase656. Thus size alone cannot discriminate;85 positive count pairs satisfy K+3S=256 under fixed layout assumptions. Actual sectorbase680 independently supplies K64; authenticated loop bound64 supplies S64. This closes count64/64 within the pinned source/layout candidate, not arbitrary revisions/configurations. Nearby name-limit and parent alternatives remain distinct evidence questions.

Sector last-hit and poisoned-index64 miss each make exactly64 predicted four-byte addr reads, return index63 orNULL, preserve database/SP/r4 and stop at return sentinel. They execute no external provider.

KV last-match and full-cache replacement each visit only slots0..63; source and stock compare all512 cache bytes. Prefix168bytes and sector/guard1624bytes remain unchanged; SP/r4-r7 and return PC are verified. Guest write hooks restrict cache writes to[db+168,db+680), stack writes to[SP-256,SP); database reads are constrained to cache range. Readable poison atdb+680 is not accessed. Guards cover these selected initialized cases; they are not proofs of safety for arbitrary inputs or all mapped memory.

Complete unchanged update_kv_cache body is extracted from authenticated candidate source. Native projection uses logical64-node scalar fields and deterministic CRC77770000; original sole reached provider585840 is intercepted with seed0/name pointer/length4 checked. Layout is supplied separately by ARM probes. This is not a compiled full ARM source identity test or CRC algorithm/collision verification. Source update behavior is closed for the two selected states; no initial inactive-slot or other replacement-tie/activity-wrap cases are executed here.

## Exhaustion boundary

Do not count these independent replays as additional canonical firmware coverage. Cache counts are now supported by offsets/bounds rather than inherited64/64claims or stride alone. Initialization, find_kv, storage/status/FAL providers, locks, concurrency, physical NOR delivery, compiler identity and byte-equal reconstruction remain open. Await implementation-owned provider/name-limit cases; no repeat of these sealed boundary cases is needed without a new discrepancy or input class.

Owner: g2/analysis/source-discovery-parallel-2026-10-09/flashdb-cache-counts-20261010/REPORT.md. Independent artifacts: results.json, checks.json, check.py, source-projection.c/dylib, and both layout directories.
