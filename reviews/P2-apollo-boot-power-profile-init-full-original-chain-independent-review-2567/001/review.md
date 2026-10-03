# Independent review 2567

**Result: PASS_SCOPED.**

The exact candidate `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-power-profile-init-full-original-chain-2566/001` binds to the pinned flash and ITCM images. Receipt, artifact, image and initializer body hashes match. An isolated replay passed all six cases.

This composition executes the original initializer, original 20/5/1-word information-read/copy chain and the original `0x41CC04` runtime leaf, with no firmware function interception. The three guard configurations and two starting register patterns check the complete 112-byte state image, installed dispatch pointer, call arguments, runtime’s seven ordered MMIO writes, return status, SP and preserved high registers. The parent returns 0 while ignoring the runtime leaf’s incidental R0 register address. The memory-write hook is bounded to `0x40008000..0x40008FFF`; it records peripheral writes without intercepting the RAM clear/copy writes.

The source payloads are deterministic fixture memory, not authenticated factory contents. The packet does not establish real peripheral effects/startup, factory data, enclosing ownership, other revision profiles or concurrent changes. This closes only the controlled child seams for this local path; no whole-firmware or canonical claim is made. Private evidence only; accepted:false.
