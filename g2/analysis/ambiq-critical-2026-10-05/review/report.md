# Independent review: architectural PRIMASK profile

## Result

No critical issue found. The real-critical profile replaces only the critical-entry seam; it executes the selected original and compiled `MRS PRIMASK; CPSID i; BX LR` function, then verifies mask state during queue-index/address reads and restoration at the call boundary. The delay seam remains synthetic.

## Evidence and checks

- `am_hal_interrupt_master_disable` in `ambiq_interrupt_mask.c` matches the pinned GNU naked-function excerpt hash in `INTERRUPT_MASK_PROVENANCE.json`. The linked function is byte-identical to the selected stock leaf at `0x473940` for all 8 bytes (`eff3108072b67047`). A GNU alias maps `opencfw_cmdq_critical_enter` to the same function without another wrapper body. The public `ambiq_interrupt_mask.h` declares the routine and states the privileged old-mask/restore contract, configurable-interrupt scope, and lack of scheduler/NMI/wall-clock guarantees.
- The final `comparison-interface-final.json` is PASS, `real_critical=true`, with 435 cases and `exact_compiled_critical_match_bytes=8`. Verifier, ELF, and source-manifest hashes match the current files. Across term cases where the index and address registers are read, the verifier observes both accesses with PRIMASK 1; it exercises prior mask 0 and 1 and confirms the original value is restored. Direct critical-entry cases confirm the returned prior value and that PRIMASK remains set after the disable call.
- The verifier keeps the delay function as the only intercepted helper in real mode. It asserts that executed code comes from an executable ELF segment, authenticates selected original-image pages against the locked firmware hash, and checks the compiled critical leaf against stock bytes.
- `ambiq-critical-simulator` uses a separate default build directory and the new header is a declared ELF prerequisite. The final report binds both source and header hashes. The Make profile stamp/force input handles profile changes when a caller reuses a directory; the regression test switches real → synthetic → real in the same directory and checks linked symbol presence. The forced rebuild makes that small target rebuild on each invocation, a minor incremental-build cost that prevents stale-profile reuse.
- `python3 -m unittest g2.tests.test_ambiq_mspi g2.tests.test_ambiq_mspi_lifecycle g2.tests.test_ambiq_mspi_cmdq -v` passed all 11 tests, including the same-directory profile-switch regression and pinned interrupt-function excerpt check.

## Limits

The provider requires privileged execution; the source comment and provenance record state this precondition. Unicorn exercises the instruction and serialized PRIMASK state, not real interrupt delivery, pending-interrupt scheduling, unprivileged enforcement, or interleavings. The test confirms the critical reads are masked and prior PRIMASK is restored, but does not prove elapsed delay or ROM timing; the delay provider remains intercepted. This remains an offline callable module, not a board startup or firmware integration claim.

## Snapshot identities

- `ambiq_interrupt_mask.c`: `27a574d24f61bf1bec7a13d16bc3e1f0816c35045f384b5ad85d808871f6a9eb`
- `ambiq_interrupt_mask.h`: `76e92c27af92ed403326c65acdbb890dccfb4f00788f06c6c99f09e4ec0de98a`
- `INTERRUPT_MASK_PROVENANCE.json`: `1394f2c876b276aa536f9b008e7e0a688cb5311b1f2e85fb9a4c6d332dbf9210`
- `simulator/verify_cmdq.py`: `99875b33236aa7b62387c744d4f898b99979320fb937a6ab2cb383660c186093`
- `Makefile`: `e5646284e96e137b3d67c54877991eb609213fcc4f9fe9dec2da3c9e197a9e27`
- `README.md`: `ea6d336538094a4d00850d47d38de2f3f8720d37853f79eeaf046aeb51ae88ee`
- real-profile ELF: `d2a2d858daac6bf54d6d3acf526cbb4931fb739469c1c0df88c3a5bb5fd7680c`
- comparison: `5a37a92ca0d9d3805f49182b757c923581b24dfc87bc480d314f2cebfc9a3595`
