# Independent review 2569

**Result: PASS_SCOPED.**

Candidate `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-power-callback-initializer-original-profile-2568/001` is pinned to the locked flash and decoded-ITCM images. Receipt, artifact, body `[0x41CE52,0x41D0EE)` and literal-pool `[0x41D11C,0x41D1C0)` hashes match. An isolated replay passed all 16 cases.

For the tested revision-24/FF AD profile, the original initializer clears the 60-byte callback table, installs the expected 15-word table and flag bytes, executes the selected callback, and then runs the original profile initializer and runtime register leaf without firmware-call interception. The assertions cover neighboring table sentinels, the 112-byte state image, dispatch/callback result, the seven ordered runtime MMIO writes, status, SP and high-register preservation. The memory-write hook is limited to the modeled peripheral span so RAM clear/copy operations remain original.

Fixture source contents and MMIO are synthetic, and flags/revision remain stable. This does not establish factory payloads, physical hardware timing/effects, concurrent mutation, startup or incoming ownership, nor other profile branches or callback implementations. The joined evidence is bounded to this AD profile. Private evidence only; accepted:false and no canonical admission.
