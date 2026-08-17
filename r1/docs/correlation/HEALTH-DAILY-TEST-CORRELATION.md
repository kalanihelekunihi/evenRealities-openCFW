# R1 health-daily synthetic test fixture

## Decision

The former largest unknown at `0x0008B378` is a 1,344-byte R1 product test fixture, not a
health algorithm or third-party provider body. Its exact diagnostics name `health_daily_test`,
`hr_daily`, `spo2_daily`, and `temp_daily`; it accepts type 0/1/2, fills selected hourly daily-cache
slots with pseudorandom synthetic values, stamps the first generated slot, and prints all 24 hours.

The exact 14-byte internal event-15 gate at `0x00042860..<0x0004286E` requires a non-null nine-byte
record and then tail-calls the fixture. Its SHA-256 is
`6b65c9e2c9e103d6d16da41f0d7d0d5eb9c1c249ae4aca2d1a44af826a133fcc`.
Internal reachability is therefore proven, correcting the earlier callerless/dormant conclusion.
OpenR1 implements only `r1_health_daily_test_event_valid`, the pure null/length decision; it does
not compile the fixture into the source-built target and exposes no event sender, payload encoder,
command registration, UI action, or synthetic health-data injector.

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
python3 tools/evidence/summarize_r1_health_daily_test.py
```

The census emits no provider source and performs no live write. Ownership is
`r1_product_specific` / `clean_room_behavior_only`, with production inclusion intentionally false.
