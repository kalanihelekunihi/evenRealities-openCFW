# Independent review 2487

**Result:** PASS_SCOPED.

Candidate `analysis/touch-mode-seven-original-builder-dispatch-2486/001` has receipt SHA-256 `51f4a42904a8735865b0b56da072894a21cc1d97c2ac498c98f9db9bd0fede3a`; its artifacts and two owned root spans validate. Isolated replay passes all 96 fixtures.

All exercised firmware routines run as original instructions, including 6AC0, 68EC, both 56A4 builder paths and their dependencies, loader, reset, status wait, and delay. The bounded fixture uses zero-initialized valid mapped rows and empty primary/secondary lists, with separate normal and type-7 descriptor buffers. Full builder write ledgers and output buffers, constructor arguments/order, delay count, final mode/status, cfg flags, and R4–R11/SP are asserted. The prior-mode-7 equality path is also checked to bypass builders and writes.

**Limits:** The mapped-row cases are deliberately narrow; more complex row branches and nonempty lists remain open. Captured non-builder register writes are diagnostic, not fully asserted. MMIO/readiness/timing are modeled. Root spans do not by themselves assign ownership to every executed dependency. Accepted:false; private scoped evidence only, no canonical admission.
