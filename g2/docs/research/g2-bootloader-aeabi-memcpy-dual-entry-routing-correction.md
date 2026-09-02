# G2 bootloader Arm EABI memcpy dual-entry routing correction

Date: 2026-09-01

## Result

The authenticated stock memcpy span `[0x0041568C,0x00415732)` has two live
Thumb entry points, not one. A whole-image halfword scan pins 33 direct callers
to the general entry `0x0041568C` and 29 direct callers to the aligned entry
`0x004156AC`. No other halfword in the 166-byte span has direct ingress.

The former single whole-span redirect replaced the aligned entry with NOPs.
The production overlay now splits the same span into two non-overlapping patch
contracts: 32 bytes at `0x0041568C` (SHA-256
`e0294160ea267d7f79540d517dc72e5a084496cbd167c0d301640609f78a810f`)
and 134 bytes at `0x004156AC` (SHA-256
`e23d4858d3544f196ab6b0b89510165e191a9364c4167192e9508e7cb36c8d0c`).
Each entry independently branches to the same source-owned forward-copy loop at
`0x00434830`.

The corrected Apple provider is 163,840 bytes with SHA-256
`13e2cee5351e5767d0cfc053025e7456a0771335086736a02e543f82adbb474b`.
The Linux provider is 163,824 bytes with SHA-256
`11f12f80ce187fce53f37b2d27bf9326a8374e1b62a061394e39c511a21b1875`.
Both were built without hardware operations. Physical boot-path confirmation
for all 62 callers is **blocked by unavailable physical evidence**.

