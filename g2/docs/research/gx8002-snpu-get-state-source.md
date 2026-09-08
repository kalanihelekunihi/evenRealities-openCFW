# GX8002 SNPU state query

The stock routine at package offset 0xf3b4 (runtime 0x10205e28) loads the
word at 0x20027350 into r0 and returns. The pinned NationalChip SDK commit
8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5 declares gx_snpu_get_state as
returning GX_SNPU_STATE (IDLE=0, BUSY=1, STALL=2). The reconstructed C uses
that authenticated header and a volatile state object. Its ABI assertion
requires a 32-bit enum.

Native macOS C-SKY compilation emits 12 bytes, exactly matching the stock
routine including compiler-generated literal and alignment padding. SHA-256:
e0db1e81ec121e7e298e9e4a1729e274737e52a23ffac3318f1cf38986de80ae.
The verifier structurally requires the three executed instructions: address
load into r3, one word load into r0, return. This proves one read, no writes,
all 32 loaded bits returned and no callee-saved register changes. Four tests
pass, including wrong address, store substitution and wrong return-register
mutations. No input value enumeration is needed for this straight-line load.

The routine is registered; integration is pending. It does not establish
ownership of all state writers or hardware scheduling correctness. SDK
snpu.o is an identity reference only and supplies no firmware payload bytes.
Adjacent code at 0xf3c0 is already covered by the analog source qualification.

Integration completed with597passing tests. The full macOS apple-clang
package was rebuilt to refresh flash-plan metadata and verify-artifacts
passed. Codec/package payload hashes remain unchanged, because the C getter
is byte-identical. The codec now has184 C functions/200 occurrences and
310,780 retained stock bytes; source-only completion remains unachieved.
