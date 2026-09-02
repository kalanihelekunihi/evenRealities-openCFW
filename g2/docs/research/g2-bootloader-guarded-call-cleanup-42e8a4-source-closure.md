# G2 bootloader guarded-call cleanup source closure

Date: 2026-09-01

The complete 30-byte function at `0x0042E8A4` is MIT production C in
`runtime_guarded_call_cleanup_42e8a4.c`. It forwards five arguments through
the callback held at control-table offset four, preserves the callback result,
then writes control/status cleanup values in the exact order `C3, 0, 0` at
offsets `0, 0x1C, 0` from `0x40014008`.

Both reviewed Arm compilers reproduce the authenticated function without
relocations, and the Apollo-main analogue at `0x00541B7C` is byte-for-byte
exact. A portable model verifies argument forwarding, return preservation,
and the ordered three-write cleanup trace.

The callback-table and control-register transaction on a live device is
**blocked by unavailable physical evidence**. No MMIO, flashing, reset, or
completeness claim occurred.
