# Independent review 2579

**Result: PASS_SCOPED.**

Candidate `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-power-callback-initializer-original-packed-profile-2578/001` binds to the pinned flash and decoded-ITCM images. Receipt, body `[0x41CE52,0x41D0EE)`, literal pool `[0x41D11C,0x41D1C0)` and artifact hashes match. The isolated replay passed all eight cases.

The tested A9 profile selections (revision `0x22`/secondary 2 and `0x23`/secondary 1) run through original table initialization/clear, the original packed-state callback, original source/copy helpers and original runtime register leaf, with no firmware-call interception. The checks include full callback table and profile-state buffers, flag bytes, first callback target, exact source arguments, initializer MMIO effects, runtime seven-write ledger, status, SP and preserved high registers. Feature bit 0 activates the five initializer writes; feature bit 1 suppresses them.

Information payloads and peripheral state are deterministic fixture memory, not authenticated factory data or physical hardware. Revision/flags are stable. Other revision profiles/callbacks, concurrency, startup and enclosing ownership remain unresolved. Private evidence only; accepted:false and no canonical admission.
