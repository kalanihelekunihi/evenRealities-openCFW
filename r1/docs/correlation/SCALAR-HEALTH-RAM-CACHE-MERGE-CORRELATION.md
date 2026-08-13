# Scalar-health RAM-cache merge correlation

The twin 364-byte functions `0x0003FEF4..<0x00040060` and
`0x000440C4..<0x00044230` are R1-owned heart-rate and SpO2 current-RAM history
orchestration. Their recovered SHA-256 values are respectively
`723e050917b4559d3378ac66c5a31635fbffd4a31af444c14cfe352b0c3b1b3e` and
`6b64439ca9d0f871794294f8ba83f089ff975ed440fe8ac8ab114df4e00d832f`.
Their sole direct calls are the `BL` instructions at `0x0008C48E` and
`0x0008D0A0` in the corresponding public history-sync paths. Both functions
are classified `r1_product_specific` / `clean_room_behavior_only`.

Both routines perform the same metric-neutral policy. They require a non-null
day builder and nonzero requested day, sample the external firmware clock, and
proceed only when the requested window start strictly precedes that clock.
They obtain the metric's daily cache through its external accessor, refresh
the requested local-day start and current UTC offset, temporarily select
acknowledgement mode 2 (`current RAM`), and reset a sparse 24-hour builder.

Each cache slot contains UInt8 average, maximum, and minimum values. A zero
average suppresses the slot. The current hour is `(now - day) / 3,600`, capped
at 23, and remains eligible outside the requested window. Every other slot is
eligible only when its hour timestamp is in the inclusive `[window, now]`
range. Selected packet records contain four bytes: hour plus the three scalar
values. The greatest selected timestamp is clamped to firmware time for
acknowledgement. A nonempty builder is flushed, and its prior acknowledgement
mode is restored.

The shared clean-room `r1_health_u8_ram_cache_merge` implements only this
selection, metadata, acknowledgement, and typed packet-handoff behavior. It
rejects a requested day later than firmware time to avoid unsigned subtraction
wrap; valid-input behavior is unchanged. It does not calculate heart rate or
SpO2. Biometric production, time/calendar services, cache ownership, logging,
storage, allocation, encoding, and transport remain provider seams. No Nordic
SDK or third-party implementation body is copied.

The Nordic SDK 17.1.0 image retains `r1_health_u8_ram_cache_merge` at
`0x00034CD8`. The verified unsigned image contains 94,804 bytes of text, 236
bytes of data, and 132,544 bytes of BSS; its 95,040-byte BIN has SHA-256
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`, and
the HEX SHA-256 is
`48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf`.

Reproduce the evidence with:

```sh
python3 tools/evidence/summarize_r1_scalar_health_ram_cache_merge.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
