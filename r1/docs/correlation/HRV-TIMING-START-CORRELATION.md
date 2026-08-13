# HRV timing-start correlation

The 382-byte function `0x00049F0C..<0x0004A08A`, SHA-256
`3bb468fcdc552cc184a6433e9cea379e4eeb751b8526effa6f037cca14c99516`,
is R1-owned HRV timed-window orchestration. It is called at `0x00049B30`
and `0x00049E4C`. Its disposition is `r1_product_specific` /
`clean_room_behavior_only`.

The start path requires mode 1, two clear transition flags, enabled health,
an external timing-eligibility result, and no existing timeout or sensor-stream
registration. An hourly request schedules a 120-second one-shot timeout. A
catch-up request reads the provider clock and suppresses the start during
second 3,450 through 3,599 of an hour; exhaustive phase evaluation shows that
all other phases also select 120 seconds. The stock function passes delay times
1,000 to the timeout provider.

After timeout creation it clears a 208-byte R1 workspace and registers one
sensor stream. Registration failure deletes the newly created timeout. The
clean-room `r1_hrv_plan_timing_start` function expresses those gates, timing,
and rollback obligations without creating a timer or registering a stream.
Time, timer, logging, sensor-stream, and biometric implementations remain
external provider boundaries.

The planner is retained in the unsigned Nordic SDK image at `0x0003518C`.
That image contains 90,956 bytes of text, 236 bytes of data, and 132,456
bytes of BSS; its standalone BIN is 91,192 bytes. The HEX and BIN SHA-256
values are `0954a9375874ee4f88139ba6243e20e1afba122e67afccba9d410e638053fa81`
and `31f3a97de9805239b03c51297f1de2ea9eaeff6fee372f1ea1f0c0a5c2f7bc91`.

Reproduce with:

```sh
python3 scripts/firmware/summarize_r1_hrv_timing_start.py
python3 scripts/firmware/build_r1_source_ownership.py --check
python3 scripts/firmware/verify_openr1.py
```
