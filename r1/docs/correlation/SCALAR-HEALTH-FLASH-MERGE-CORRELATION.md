# Scalar-health flash-record merge correlation

The two 394-byte functions at `0x00040508..<0x00040692` and
`0x000446B4..<0x0004483E` are the R1 heart-rate and SpO2 variants of one
FlashDB history callback. Their SHA-256 values are respectively
`3b8c05a2fbc91de8a2f04a792ade31957920c04cc21289031f8074bd5b74a1ad` and
`a215fc2a880381053c078871467e153f22d9bfd8d7f68c2b667c74a06c017257`.
Neither has a direct branch caller because both are passed to the FlashDB
iterator. Their disposition is `r1_product_specific` /
`clean_room_behavior_only`.

Both callbacks require an exact 128-byte record, reject timestamps newer than
firmware time, and delegate UTC-to-local conversion to the existing calendar
provider. Local hour zero maps to slot 23 and subtracts 86,400 seconds from the
derived day; all other hours map to `hour - 1`. An optional synchronization
filter admits only records earlier than the current local day.

The three-byte scalar tuple is average, maximum, and minimum. A zero average is
ignored. A populated builder is flushed when day or timezone changes, then
reset before insertion. The first record for an hour wins, while the newest
record timestamp advances even when a duplicate slot is ignored. Each present
slot encodes as four bytes: hour plus the three scalar values.

The clean-room `r1_health_u8_flash_record_merge` implementation is shared by
heart rate and SpO2 and consumes a normalized record containing the provider's
calendar result. It implements the R1-owned filtering, day grouping, duplicate
policy, flush boundary, and monotonic acknowledgement cursor. FlashDB blob
reading, calendar conversion, logging, transport, and biometric algorithms are
not reimplemented.

The shared function is retained in the unsigned Nordic SDK image at
`0x000349D0`. The image contains 90,956 bytes of text, 236 bytes of data,
and 132,456 bytes of BSS. Its standalone BIN is 91,192 bytes. The HEX and
BIN SHA-256 values are
`0954a9375874ee4f88139ba6243e20e1afba122e67afccba9d410e638053fa81` and
`31f3a97de9805239b03c51297f1de2ea9eaeff6fee372f1ea1f0c0a5c2f7bc91`.

Reproduce with:

```sh
python3 scripts/firmware/summarize_r1_scalar_health_flash_merge.py
python3 scripts/firmware/build_r1_source_ownership.py --check
python3 scripts/firmware/verify_openr1.py
```
