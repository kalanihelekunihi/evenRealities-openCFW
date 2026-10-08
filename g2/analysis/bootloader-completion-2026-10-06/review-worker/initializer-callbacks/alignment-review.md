# Thumb alignment checker review

Independent receipt: `alignment-review.json`.

The checker in `thread_creation/verify_code_alignment.py` inspects executable-section symbol records. It rejects any ARM `$t` mapping symbol whose address is odd and rejects any `STT_FUNC` symbol without the Thumb low-bit tag. Against the DCE image it accepted 331 `$t` mappings. Against the known-bad AC4B image it rejected `$t` at odd `0x31a9b` in `.source_cache`, reproducing the misaligned entry that led to an invalid SVC. DCE's ELF audit found nonempty executable sections all had at least one `$t` mapping.

The linker correction addresses the demonstrated failure at two levels: `ALIGN(4)` before each selected `.source_cache` object prevents a preceding odd-length input object from shifting the next object start; `.p2align 1` in the local Thumb wrapper ensures its function begins on a legal halfword boundary. The checker correctly requires even actual `$t` addresses rather than confusing the odd Thumb-tagged `STT_FUNC` value with the instruction address.

On the next pinned candidate, root strengthened the checker to require at least one `$t` mapping in every nonempty executable section. Independent follow-up receipt `alignment-review-4598.json` confirms this check passes the 4598 ELF with 331 mappings and continues to reject AC4B at the odd mapping `0x31a9b`. The checker validates ELF placement metadata only; it does not validate opcode correctness, control flow, architectural behavior, or hardware boot.

Pinned evidence:

- DCE ELF SHA256: `dceae3b56c3ef4b0572f4cd499230ca8f5eb20419cf1c4a0910d05d607389bee`
- 4598 ELF SHA256: `4598040563d8f41b2fc71d430114b6b8564198b439e7225e9729d2f1c93acc2e`
- AC4B known-bad ELF SHA256: `ac4b5688528586d9d49d332203d4f31985d2ca939728f7cf6cbb51dc951afb51`
- Current checker SHA256: `71aeddccdb33ffa7179181630f0eae788000d94360c0274274918a3f2a94af2f`
- Linker source: `thread_creation/startup_source_image.ld`, object boundaries and alignment around lines 174–216
- Wrapper source: `nor_commands/nor_timing_wrapper.S`, `.p2align 1`
