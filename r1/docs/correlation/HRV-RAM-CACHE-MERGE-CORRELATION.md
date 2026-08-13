# HRV RAM-cache merge correlation

The 380-byte function `0x00040DE0..<0x00040F5C`, SHA-256
`146d9efe6adcee580a40d9427899f358d4f9cd8e7552041ab9be041277da0fe5`,
is R1-owned HRV current-RAM history orchestration. Its sole direct call is the
`BL` at `0x0008CA90` in the public HRV history-sync path. Its disposition is
`r1_product_specific` / `clean_room_behavior_only`.

The function requires a non-null day builder and nonzero requested day, samples
the external firmware clock, and proceeds only when the requested window start
strictly precedes that clock. It obtains the HRV daily cache through an external
accessor, refreshes the cache's requested local-day start and current UTC
offset, temporarily selects acknowledgement mode 2 (`current RAM`), and resets
the sparse 24-hour builder.

Each cache slot is six bytes: UInt16 average, maximum, and minimum. A zero
average suppresses the slot. The current hour is `(now - day) / 3,600`, capped
at 23, and is eligible even outside the requested window. Every other slot is
eligible only when its hour timestamp is within the inclusive `[window, now]`
range. Selected records occupy seven bytes in the packet: hour plus those three
UInt16 values. The greatest selected timestamp is clamped to firmware time for
acknowledgement. A nonempty builder is then passed to the already bounded HRV
flush path, and the prior acknowledgement mode is restored.

The recovered flush adds a fixed six-byte latest-HRV prefix after the
count/timezone/day header. The clean-room `r1_health_u16_ram_cache_merge` copies
the typed cache's latest value and timestamp into that existing daily-UInt16
encoder seam, emits one packet, and resets the workspace after the attempt. It
also rejects a requested day later than firmware time to avoid the stock
unsigned subtraction wrap; valid-input behavior is unchanged.

This closure implements no HRV calculation. The HRV producer, time/calendar
provider, cache ownership, allocation, transport, logging, and storage remain
external provider boundaries. No Nordic SDK or third-party implementation body
is copied.

The clean-room merge is retained in the unsigned Nordic SDK image at
`0x00034CF0`. That image contains 94,804 bytes of text, 236 bytes of data, and
132,544 bytes of BSS; its standalone BIN is 95,040 bytes. The HEX and BIN
SHA-256 values are
`48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf` and
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_hrv_ram_cache_merge.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
