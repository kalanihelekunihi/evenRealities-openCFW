# Independent review: bounded Ambiq CMDQ disable/termination

## Result

No critical correctness defect found in the reviewed snapshot. The selected CMDQ disable and forced-term bodies are exact text matches to pinned public Ambiq source; the bounded source implementation agrees with authenticated original instruction execution across 372 cases. The source and evidence correctly keep reconstructed index refresh and synthetic critical/delay providers distinct from exact source reuse and hardware behavior.

## Findings

- `am_hal_cmdq_disable` and `am_hal_cmdq_term` excerpt hashes match the pinned source and are covered by `CMDQ_PROVENANCE.json` plus `test_ambiq_mspi_cmdq.py`. The Ambiq 2025 BSD notice is preserved in both derived CMDQ files.
- The ARM32 CMDQ state view asserts `pReg` at `+0x24`; the reconstructed register table uses the first five stock register pointers and pause mask. This is a sparse compatibility contract, not an initializer or general HAL state. CMDQ handles/register pointers must already be valid; neither selected upstream function validates those pointer fields.
- `update_indices` follows the observed stock sequence: critical-entry provider, read hardware index low eight bits, combine with `endIdx` high bits, wrap backward by 256 when the signed difference is negative, read CQ address into `cmdQHead`, and restore PRIMASK. It is a bounded reconstruction rather than an exact copied function body. All 64 original bytes of its stock range execute in the comparison corpus.
- The two MSPI shims preserve the important distinction: disable loads a CMDQ handle from the caller's local `+0x828` slot; termination reads the module index and loads from the fixed stock global base `0x200523d8 + module * 0x8d0 + 0x828`. The termination shim passes force=true, ignores the CMDQ term result, clears the global slot, and returns success, matching the authenticated original shim. Tests include separate local/global slot values.
- `comparison-reviewed.json` is PASS with 372 cases. The verifier hash, linked ELF hash, and each C/H/LD source-manifest hash match the current files. It covers all three modules, valid/invalid/null CMDQ handles, enabled/already-disabled paths, forced/nonforced term, busy/nonbusy indices, 8-bit index masking and wrap, local/global null slots, pending MSPI state, and XIP. All seven original function bodies/ranges are fully executed (472 unique original instruction bytes, including the earlier 174-byte lifecycle set). Code-hook fetch validation now requires the ELF segment's executable flag.
- Critical-entry and delay seams are intercepted on both sides. The fixture does not mask interrupts or wait; this proves neither real PRIMASK timing nor queue completion/free behavior. The fixed global-state address, module range, pointer validity, and caller concurrency remain integration preconditions.
- `python3 -m unittest g2.tests.test_ambiq_mspi g2.tests.test_ambiq_mspi_lifecycle g2.tests.test_ambiq_mspi_cmdq -v` passed all 9 tests. The CMDQ test locates `arm-none-eabi-nm` via PATH and skips that symbol check when the utility is unavailable.
- The component README now describes the six MSPI functions and a bounded CMDQ provider profile, explicitly distinguishing the real CMDQ subset from the older synthetic provider profile and stating the no-interrupt-safe-driver/no-hardware limits.

## Snapshot identities

- `ambiq_cmdq.c`: `39dfd4515413e88e66b07f8eea47664a6d666943069e65768f1a284435583a24`
- `ambiq_cmdq.h`: `8f4dffc5e3cf2b33cf877dab9ba5b2841b74451a379b9ab49ab4ec0d2869ce7d`
- `simulator/verify_cmdq.py`: `a0c432bfec979587256443d87e6d3c6a1e632a434614180a34d93ced4eb8dcd9`
- `CMDQ_PROVENANCE.json`: `de3ade604a704200d9b86ead4b8d28764e913cb80882c8c05ea8a755a6591430`
- `test_ambiq_mspi_cmdq.py`: `79fcdfdb57da792fb300514bab0effd2aca62a52dc6184772bf9ab1c9a1e1aff`
- `Makefile`: `66d3ac2fb0e77e21fa6cd40c6d1febdba198e0889fa68429ada2a9528ad30076`
- linked ELF: `58a408255d1f4e5974c443c0513e7a4b908ad1570fff3976dd04c5bc5846e1f6`
- reviewed comparison: `90abec0eaa8aeb600586ac7b89c4743aeb2b74ebcaf18621ea6f24ff4e28928a`
