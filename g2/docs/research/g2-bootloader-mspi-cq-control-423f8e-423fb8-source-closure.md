# G2 bootloader MSPI command-queue control source closure

The adjacent bodies at `[0x00423F8E,0x00423FAC)` and
`[0x00423FAC,0x00423FB8)` are the AmbiqSuite 5.1.0 static helpers
`mspi_cq_enable` and `mspi_cq_disable`. Their authenticated stock SHA-256
values are respectively
`b846c512f60e83e86f69d04322eb6ce0d5936f143ad86475967c6be67545ab65`
and `8c21c4878a3125546a7201b39610d661f69d8da7e1cae81d3eb223fdf919fb0a`.
Their identities and behavior close against the unmodified BSD-3-Clause
`am_hal_mspi.c` from commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`, Git blob
`c12ef914660227aba3ebef3a0fb3ec749510c1bc`.

## ABI and behavior

`mspi_cq_enable` reads the 32-bit module at state offset four, converts
`AM_HAL_CLKMGR_USER_ID_MSPI0 + module` to the stock one-byte user-ID ABI, and
requests clock ID four through the already source-owned routing entry at
`0x004222F0`. A nonzero clock result is returned without enabling the queue.
On success, the handle at state offset `0x828` is passed to
`am_hal_cmdq_enable` at `0x00427878`, and that provider status is returned.

`mspi_cq_disable` passes the same handle directly to `am_hal_cmdq_disable` at
`0x004278C8` and returns its status. Neither private helper adds handle or
module validation beyond the upstream behavior.

The shared MIT clean-room target source is 2,420 bytes with
SHA-256
`2b52b27e06cc9e07c464991a139ea2f424d024334a88f9060e989e96f42b18ff`.
The 30-byte enable section has unrelocated SHA-256
`cd2e0ce6c18ac97d1fd1472f24ac2c10cc4a44f2975133178e19d17b4d1411f0`
and two `R_ARM_THM_CALL` relocations: offset `0x0C` to `0x004222F0` and
offset `0x18` to `0x00427878`. The 12-byte disable section has unrelocated
SHA-256
`e701bdc5d633faefd76b340e85ef86e0099177411ae4c6a202515a211c684fc1`
and one `R_ARM_THM_CALL` relocation at offset `0x06` to `0x004278C8`.
After relocation, both reviewed Clang profiles match their stock intervals
byte for byte.

## Provider and redistribution boundary

The authenticated BSD-3-Clause `am_hal_cmdq.h` declares the retained provider
ABIs `uint32_t am_hal_cmdq_enable(void *pHandle)` and
`uint32_t am_hal_cmdq_disable(void *pHandle)`. The header is 10,496 bytes,
SHA-256
`0113aed2f109c5f022d38055b83a75c2cf141e8621177296757fc8315926762f`,
and Git blob `9baaf36c6c4e906602b76abf45f5d90e33451ce0`. The provider bodies remain
official-package bytes rather than source-owned entries. Their official
binary redistribution authority is unresolved; community distribution must
continue to obtain them from an authenticated package supplied locally by the
user.

Focused host tests cover clock success/failure ordering, returned provider
statuses, handle forwarding, the one-byte user-ID conversion, and both target
profiles. The component builder pins the exact source, relocation, linked
body, and stock hashes. Hardware validation is blocked by unavailable physical evidence;
future authorized physical qualification remains required.

Waves 7 and 8 subsequently admit the 134-byte `mspi_cq_pause` and 108-byte
`program_dma` successors through `0x004240AA`, moving the current retained
interval to the `sched_hiprio` frontier. See
`g2-bootloader-mspi-program-dma-42403e-4240aa-source-candidate.md`.
No hardware, MMIO, flashing, signing, or publishing operation was performed.
