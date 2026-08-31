# G2 bootloader MSPI controller-configure source closure

The authenticated `am_hal_mspi_configure` body occupies
`[0x00424AF0,0x00424BD4)` (228 bytes; SHA-256
`7e844f8b690703208e8e932371914cc19506c0d8adf682bfe03a28e55357ad8c`).
Its sole direct caller is `0x004202EE`. The preceding alignment and state-base
literal remain retained data.

Production now routes a 152-byte structured BSD-3-Clause C return path at the
authenticated entry. Apple Clang 21 and Homebrew LLVM Clang 22 emit identical
bytes (SHA-256
`f48e9bead432163e13d495026fb798ea87c640638ea6ec79bfa179a3d766bad1`)
with two-byte alignment and zero relocations. The replaced stock prefix hashes
to `2b81ab47153b316f2a0d1803cdf2a36eda6c7d4aa57125c878f6d8d032836862`.
The source contains neither an executable `.byte` transcript nor inline
assembly. Its return leaves the remaining 76 stock bytes unreachable and
retained rather than relabeling them as source.

The recovered state ABI validates the allocated `0x01BEBEBE` handle prefix and
rejects an enabled controller. It clears `DEV0XIP.XIPEN0`,
`DEV0SCRAMBLING`, and `DEV0AXI` at per-module MSPI base
`0x40060000 + module * 0x1000`; records the TCB address and size; derives the
TCM-boundary flag and capped 256-entry queue capacity; and writes clock-on-D4,
configured, and 26-mode fields. Host tests cover valid and invalid handles,
enabled state, null TCB, strict TCM boundary, unsigned-small-size behavior,
capacity capping, exact MMIO offsets, and non-mutation on rejection.

Apple bootloader accounting is now 29,103 source-owned, 16,490 generated, and
118,247 retained official bytes across 591 manifest intervals. Apple/Linux
provider identities are respectively
`52a74441ebb82b7127833f6de4d1068e880ccfaa416fdbe6b33f4df05e9df118`
and
`7fc80bccf1f3bd51fdffc86b0043ca7243064fff1602fbfd4f2c54203cdf9f7d`.
The unsigned packages remain complete and deterministic at 4,678,740 and
4,471,056 bytes, with SHA-256
`ab632e3d9ccaf54eb0ced23cd02b59c950fb4627bfa1844da32a4a7f4bea8b48`
and
`b73b2b107658b1503c40e2e6db9114c1b3db4e81f08778ad5c218f7b4e0e795b`.

No hardware, MMIO, reset, erase, signing, transport, or flashing operation was
performed. Live register, TCB SRAM, TCM boundary, queue capacity, clock-on-D4,
XIP, and cold-boot qualification are **blocked by unavailable physical
evidence**. The next executable software frontier is the 1,154-byte public
`am_hal_mspi_device_configure` body at `[0x00424BE4,0x00425066)`;
firmware-wide functional completeness is not claimed.
