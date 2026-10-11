# SMP CCB lookup candidate

`ccb_lookup.c` source-defines the complete bounded `smpCcbByConnId` body at 0x5375fc..0x537742. For a nonzero low-byte connection ID, it returns `ccb_base + (id - 1) * 76`. The stock function does not check `DM_CONN_MAX` on this path despite the SDK assertion text, so the candidate preserves the actual instruction behavior.

For zero ID, it reproduces the five-stage product diagnostic cascade and returns null. Logging gate, bounded comparator, flags, extended logging and trace remain explicit provider callbacks. `g2_smp_candidate_ccb_by_id(void*,uint8_t)` matches the SMP handler callback shape; its context is the `g2_smp_ccb_provider` layout in the source. A production integration must assemble this context with the handler's other callback needs and relocated literal/data identities.

The bounded source compares against original bytes in `g2/analysis/smp-ccb-candidate-20261010/verify.py`. The test scripts each external callback; it does not establish real logging output or live CCB lifetime.
