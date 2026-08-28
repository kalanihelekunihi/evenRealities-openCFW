# G2 bootloader MSPI command-queue termination source closure

The complete 58-byte body at `[0x00423F54,0x00423F8E)` is the AmbiqSuite
5.1.0 static helper `mspi_cq_term`. Its authenticated stock SHA-256 is
`07a7e8e54305fbecb7f891cd4e843881b73a33186ba1750b147e0647d0041807`.
The identity and behavior close against the unmodified `am_hal_mspi.c` from
upstream commit `5efc0228528a8adce5eae0d226fac85d2551eb3b`. That file is
168,473 bytes, SHA-256
`5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f`,
and Git blob `c12ef914660227aba3ebef3a0fb3ec749510c1bc` under BSD-3-Clause.

## ABI and behavior

The wrapper accepts the MSPI state pointer in `r0`, reads the 32-bit module at
offset four, and derives `g_MSPIState[module]` using base `0x2001CAA0`, stride
`0x8D0`, and command-queue handle offset `0x828`. A null handle returns success
without a provider call. A non-null handle is passed to `am_hal_cmdq_term`
with `bForce == true`, then the stored handle is cleared and success is
returned. As in upstream, this private helper does not add module validation.

The target implementation in
`components/bootloader/core_overlay/runtime_mspi_cq_term_423f54.c` is
MIT, 1,926 bytes, SHA-256
`bdb222fbe66f8ccbd7754e2964750c01dba482a4a6d5f6c42bd9bdb127d214e4`.
Its linked Cortex-M55 body is exactly 58 bytes and byte-identical to stock.
The unrelocated section SHA-256 is
`b74c87846388ad17a4d467d7c2727862da5356c4f3d6cfe14ed0bf2c541f39fe`;
its only relocation is an `R_ARM_THM_CALL` at offset `0x26` to the retained
provider entry `0x00427AD6`.

## Provider and redistribution boundary

The retained provider has the typed upstream ABI
`uint32_t am_hal_cmdq_term(void *pHandle, bool bForce)`, authenticated by
`am_hal_cmdq.h` (10,496 bytes, SHA-256
`0113aed2f109c5f022d38055b83a75c2cf141e8621177296757fc8315926762f`,
Git blob `9baaf36c6c4e906602b76abf45f5d90e33451ce0`) under BSD-3-Clause. The
provider body at `0x00427AD6` remains retained from the user-supplied official
package; this admission does not claim it as source-owned. Its corresponding
official binary redistribution authority is unresolved and is not inferred
from the upstream source license.

Both reviewed Clang profiles emit the same pinned target body after the one
typed relocation is applied. The component builder independently verifies
source size/hash, compiler identity, section size, relocation type/offset,
linked body hash, and equality with the authenticated stock interval. Host
tests cover null and non-null handles, forced termination, handle clearing,
and the lack of wrapper-side module validation. Hardware validation is
blocked by unavailable physical evidence; future qualification still requires authorized
responsive G2 physical evidence.

The next source-owned entries are CQ enable at `0x00423F8E` and CQ disable at
`0x00423FAC`; their shared closure ends at `0x00423FB8`. No hardware, MMIO,
flashing, signing, or publishing operation was performed.
