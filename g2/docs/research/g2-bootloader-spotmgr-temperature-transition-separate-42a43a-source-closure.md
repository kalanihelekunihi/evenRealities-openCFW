# G2 bootloader SPOT-manager stepwise temperature-transition source closure

Date: 2026-09-01

The 130-byte `spotmgr_temperature_transition_separate` body at
`[0x0042A43A,0x0042A4BC)` is BSD-3-Clause production C grounded in AmbiqSuite
SDK 5.1.0 commit `5efc0228528a8adce5eae0d226fac85d2551eb3b`.

Both reviewed Clang profiles reproduce the exact body (SHA-256
`1075e4055c2ef66d985f8938f881a08d43a90791be3dc0b2700ff7e0074ed107`)
after two strict calls to the selector at `0x0042A2B4`. The unrelocated SHA-256
is `066596bd21489fc692537d3fb5724af2ab6ba1eecb93d78b36ce35ea3a4d44cc`.
Callers are `0x0042A4F2` and `0x0042A518`; the callback-table pointer is the
authenticated SRAM address `0x20000158`. The Apollo-main analogue at
`0x005A44BA` shares 126 of 130 bytes. Host tests exhaust all 400 valid
start/end state pairs and verify every upward/downward intermediate dispatch.

Physical callback execution, voltage/temperature timing, reset, and boot
qualification is **blocked by unavailable physical evidence**. No signing,
flashing, reset, or live hardware access occurred.

