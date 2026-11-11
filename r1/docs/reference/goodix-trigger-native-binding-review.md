# Goodix interrupt-trigger native C binding

The existing stock entry `0x2e8cc..0x2e8e7` is `Gh3x2xIntPinTriggerModePro` under the checked polling configuration. REA and raw instructions show `GH3X2X_WriteReg(0x0502,0)`, followed by the tail call `GH3X2X_WriteRegBitField(0,10,10,0)`. The final branch restores the caller's frame before entering the second provider. The stock ABI takes no arguments; the earlier callback/context abstraction did not describe that ABI.

The frontier and ownership record now point to `{gen}/gh_demo_r1.c`, generated from pinned upstream source. The superseded `goodix_primitives_reset_register_fields` definition, declaration and unused operations structure were removed. Its callbacks and null-provider rejection are not part of stock behavior. This reuses the existing inventory entry; it adds no corpus coverage claim or second implementation.

Verification:

- 384 paired stock/C cases check ordered provider arguments, first-provider SP at caller minus eight, terminal-provider SP at caller, provider return-bit patterns, caller-clobber effects, saved registers and interrupt masks. Providers are modeled; provider-private save words and caller-clobbered final state are outside the comparison. R0 tail propagation describes the tested emitted void function, not an ISO C return-value promise.
- The prior normal-interrupt build is rejected because it omits the required `0x0502` write.
- All 575 units compile without failures or duplicate strong symbols; unresolved import sets remain 173/34. All 574 other objects are byte unchanged. In the primitive object, 320 other function bodies are unchanged. One function has two internal BL encodings updated to the same relocated `goodix_primitives_hr_extrema_refine` target after removal of the preceding 56-byte helper; all its remaining bytes and relocation records agree.
- Five Clang qualification profiles compile and select nothing. Four GCC9 profiles compile and select one complete 28-byte body. Its two linked provider targets and all bytes equal stock. Only that official region was appended to the canonical plan, with overlap checks.

The canonical rebuilt application equals the locked artifact SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`. Coverage is now 3,933 source-built bytes, 642,227 stock fallback bytes and 248 resource bytes. The new 28 bytes are C executable bytes. Physical register/bus/sensor operation, full initialization, global source completeness and G2 readiness remain unproven. No stock reference hash changed.

[Machine-readable evidence](goodix-trigger-native-binding-review.json) binds the REA capture, original ownership, probes, removed implementation, object audit, qualification, source plan and canonical build. Probes remain under ignored `build/goal-r1-goodix-trigger/`.
