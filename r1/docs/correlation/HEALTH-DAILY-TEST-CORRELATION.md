# R1 health-daily synthetic test fixture

## Decision

The former largest unknown at `0x0008B378` is a 1,344-byte dormant R1 product test fixture, not a
health algorithm or third-party provider body. Its exact diagnostics name `health_daily_test`,
`hr_daily`, `spo2_daily`, and `temp_daily`; it accepts type 0/1/2, fills selected hourly daily-cache
slots with pseudorandom synthetic values, stamps the first generated slot, and prints all 24 hours.

No direct caller and no code/data pointer to the entry exists in the recovered image. Production
reachability is therefore unproven, and openR1 does not need this fixture in a production image.
The behavior may be independently recreated only as an explicit test utility; it must never feed
synthetic health measurements into a production path.

## Exact scattered body

Ghidra reports one logical function whose 1,344 executable bytes occupy four ranges:

- `0x0008B378..<0x0008B686` — validation, time-window selection, and random record generation;
- `0x0008D40C..<0x0008D4C2` — 24-hour heart-rate record dump;
- `0x0008E3F8..<0x0008E4AE` — 24-hour SpO2 record dump;
- `0x0008E560..<0x0008E626` — 24-hour temperature record dump.

The concatenated body SHA-256 is
`75cfeeac1565b8d44e251089066133f06e946af53ed3a849f230787c436ee255`.
Intervening production functions and literal/string pools are excluded.

The static verifier is reproducible with:

```sh
python3 scripts/firmware/summarize_r1_health_daily_test.py
```

The census emits no provider source and performs no live write. Ownership is
`r1_product_specific` / `clean_room_behavior_only`, with production inclusion intentionally false.
