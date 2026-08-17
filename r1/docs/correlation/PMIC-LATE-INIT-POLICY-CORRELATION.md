# PMIC/NFC late-initialization policy correlation

The R1 late-initialization routine at `0x00096A7C..<0x00096AD0` is an 84-byte
function with SHA-256
`c3244e2b6c136ada745280e2d792ef78f315e56612988ea17e920e4b8afd443f`.
Ghidra omitted this entry from its function inventory; its direct caller is the
already bounded system-task startup at `0x00092512`, so the exact body is
admitted as a manual provenance supplement.

The function first clears the byte at `0x20006870`, then performs this fixed
product-orchestration sequence:

1. Acquire the NFC client of the shared `i2c_5` resource.
2. Wait 50 milliseconds.
3. Run the pinned ST25DVxxKC configuration adapter.
4. Release the shared NFC resource.
5. Run the existing charge-I2C event operation with event zero.
6. Install Thumb callback `0x00042EC5` in the YHM callback slot.
7. Install device callback `0x00042D2F` through the existing PMIC adapter.
8. Read fixed-record configuration byte `0x70`.

Only when that byte is the factory marker `0x55` does the routine schedule
callback `0x00042ED9` with context zero after 1,024 raw ticks.

`r1_pmic_late_init_plan_build` preserves this order and conditional action as a
pure plan. It does not acquire hardware, delay, initialize NFC, mutate callback
slots, or schedule timers. The pinned ST provider, reconstructed YHM boundary,
shared-resource adapter, delayed-event loop, and platform executor retain those
responsibilities.

Reproduce the exact body/hash, direct caller, nine direct-call sites, four
literal pointers, ready byte, and factory branch with:

```sh
python3 tools/evidence/summarize_r1_pmic_late_init_policy.py
```
