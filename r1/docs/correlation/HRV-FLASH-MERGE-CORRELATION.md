# HRV flash-record merge correlation

The 402-byte function `0x00041438..<0x000415CA` is R1-owned HRV history policy with SHA-256
`5dd9d6ca6503c405489a2eac90d528ac158c67d02e5961db8d0318446520e48c`. It has no direct
branch caller because it is used as a FlashDB iterator callback. Its disposition is
`r1_product_specific` / `clean_room_behavior_only`.

The callback requires an exact 128-byte record, rejects timestamps newer than firmware time,
derives local day and hour through the external calendar provider, and optionally applies the
configured synchronization window. Local hour zero maps to slot 23; other hours map to
`hour - 1`. A day is calculated from hour/minute/second, with the recovered 86,400-second
midnight adjustment.

Zero-average records are ignored. A populated builder is flushed when its day or timezone differs,
then reset before insertion. A previously populated hour is not overwritten. New records occupy
seven bytes—hour plus three UInt16 values—and the newest record timestamp advances monotonically.

This closure admits only that bounded merge policy. FlashDB blob reading, the unresolved
time/calendar provider, allocation, Nordic logging, packet flush/send, and biometric production
remain independently owned external seams. The current clean daily-UInt16 encoder already supplies
the seven-byte slot representation; no provider body is copied.

Reproduce with:

```sh
python3 scripts/firmware/summarize_r1_hrv_flash_merge.py
python3 scripts/firmware/build_r1_source_ownership.py --check
python3 scripts/firmware/verify_openr1.py
```
