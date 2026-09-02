# G2 bootloader second SPOT-manager deep-sleep scan source closure

Date: 2026-09-01

## Result

The 288-byte function at `[0x0042AEF0,0x0042B010)` is BSD-3-Clause
production C in `runtime_spotmgr_buck_deepsleep_scan_42aef0.c`, grounded in
AmbiqSuite SDK 5.1.0 Apollo510 SPOT-manager behavior at commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`.

Both reviewed compilers reproduce the exact stock body after one strict call
relocation at offset `0x30` to the STIMER-running provider `0x0041F3F0`.
Linked SHA-256 is
`7a54959ea8247c505df0f3139ce607b4d1fabb5d0015054b89bd44b5d79cc31b`;
unrelocated SHA-256 is
`040d93b977d325156b2ac09b6f01d68023fb2faf2bcf18e083a469afbb46e490`.
The direct caller is `0x0042BC08`. The Apollo-main analogue at `0x005A0C20`
shares 284 of 288 bytes; the only difference is the image-relative STIMER
call encoding. Five shared hardware literals are authenticated: SYSPLL
control `0x400204D8`, the result byte `0x200271C0`, STIMER configuration
`0x40008800`, timer instance base `0x40008000`, and timer global enable
`0x40008010`.

The scan blocks deep sleep for the authenticated temperature, peripheral,
SYSPLL, STIMER, or enabled timer-clock conditions. Its portable model passes
100,000 deterministic randomized snapshots spanning all sixteen timers and
all three clock ranges.

Actual deep-sleep entry, timer activity, SIMOBUCK behavior, rail stability,
reset, and cold-boot qualification are **blocked by unavailable physical
evidence**. No hardware operation or firmware-wide completeness claim
occurred.
