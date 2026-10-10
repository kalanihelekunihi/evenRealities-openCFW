# Independent fixed-recipe NationalChip C compiler review

**PASS: 26 independent checks.** [Structured receipt](DSP-C-COMPILER-INDEPENDENT-VERIFICATION.json) authenticates retained results without repeating compilation or executing Docker/compiler/firmware.

Verified archive SHA256 `df33d1e101d9b0c1d4cc68286bb97a98e3a3095cf321f9e253f0ddf805d8d9f9`; extracted GCC hash; original archive membership/bytes for GCC, assembler and cc1; all 452 retained SDK header hashes; five source and object hashes; five exact command vectors; parsed ELF text-section sizes and undefined symbols; and direct full-section comparison against authenticated stock codec bytes. The receipts record GCC 6.3.0, C-SKY Tools V3.10.15 Minilibc abiv2 B20190929. This resolves the prior compiler-availability boundary for this local toolchain; version agreement alone does not establish the unique producing compiler distribution.

The commands use one fixed CK804ef hard-float O2 recipe, debug information, no builtins, strict volatile bitfields and function/data sections, plus four SDK-declared include directories. No command adds feature macros. Docker commands specify network none, read-only root, read-only repository/tool mounts and the isolated writable output mount, on linux/amd64. The recorded image identity is `sha256:af35f7f439b4af1827cdbfffe1f0895540b2aaf8c6a19ff5059e4250047e37d0`; this review did not inspect the live Docker image or repeat execution. The fixed command is a candidate recipe, not proof of the original per-file build configuration.

| Selected function | Compiled C section | Stock section | Exact equality |
|---|---:|---:|---|
| shift | 368 bytes | 116 bytes | No |
| copy | 84 bytes | 44 bytes | No |
| fill | 70 bytes | 40 bytes | No |

Measured result: five of five retained C units compile; **zero of three selected comparable C sections are byte-identical** under this recipe. No normalization, padding exclusion or relocation masking is used. This selected measured zero must not be presented as zero C recovery across the entire codec.

The 56-byte CFFT and 110-byte RFFT C sections are wrappers. Parsed undefined symbols are exactly butterfly forward/inverse, `csky_bitreversal_q15`, `csky_cfft_q15`, real split and inverse real split. The missing bitreversal symbol here is `csky_bitreversal_q15`, not the independently reproduced 38-byte `csky_bitreversal_16`; those names/contracts must not be conflated. Compilation produces relocatable objects, not a linked complete transform or image.

These authentic C implementations are compilable candidates for semantic alternatives. Numerical equivalence to stock has not been established, and differing sizes/hashes alone demonstrate neither semantic failure nor equivalence. Independently authenticated assembly-source output still reproduces nine selected stock sections totaling 1,606 bytes. That source-assembly result is already the exact-byte evidence for the selected sections; this C attempt does not weaken it or convert it into C output.

## Exact remaining evidence

- For exact C output: authentic definitions for the absent kernels and a producing source revision with per-file preprocessing/macros, headers and compiler configuration that explains the stock output. A GCC version string or a broad flag sweep cannot certify this. Because the selected stock sections have matching authentic assembly sources, identical C output is not a prerequisite to using that assembly-source path in a later authorized full source build.
- For semantic alternatives: defined input/aliasing/overflow/shift contracts and bounded numerical validation against the exact stock instruction behavior. Source names and successful compilation do not establish those contracts.
- For source completeness and byte equality: resolved wrapper dependencies, exact linking/placement/relocation configuration, all remaining codec source/data and an admitted integrated locked-image build receipt. None is supplied by five successful object compilations.
- For physical/live-use claims: backup selection and CPU alias visibility remain separate boundaries; compiler receipts cannot resolve them.

The earlier six-component matrix is unchanged. Additive facts are five compile receipts and zero of three exact C section matches, alongside the existing exact source-assembly evidence. No canonical admission, source edits, device operation, Git mutation, repeated build or model switch occurred in this review.

## Additive correction — kernel source availability

The earlier “authentic definitions for absent kernels” boundary was too broad. Discovery identified four definitions already present in the pinned registered SDK: forward/inverse butterfly in `utility/libdsp/Source/TransformFunctions/csky_radix4_butterfly_q15.c`, and forward/inverse real split in `csky_split_rfft_q15.c`. Independent verification passes 26 checks; see [receipt](DSP-KERNEL-LINEAGE-INDEPENDENT-VERIFICATION.json). The prior undefined ELF references prove that these units were not linked in that experiment, not that their source is unavailable.

The DSP Makefile explicitly disables the two C kernel objects and selects their assembly alternatives while retaining C wrappers. The retained immutable public import `a47076981e6c1ac3b9b1073c3e3e9466d8de7ea8` Makefile is byte-identical to the current pinned Makefile. The three retained history responses contain that single import and reference upstream-mainline `ec66ba4f101fb8dccf0dfed92a3b0b15402dd44c`; this private/historical identifier is not acquired source. No public endpoint refetch was needed for this receipt review. Literal Makefile `CSKY_SIMID` and C conditional `CSKY_SIMD` remain distinct.

Revised boundary: the four kernel sources are available; compiling and resolving the complete C alternative is owner work now in progress. Complete C build/link receipts, numerical equivalence and exact stock identity remain separate unverified claims. Searching for source that is already registered, or assuming flag changes will make portable C reproduce hand-written assembly, is not justified. The original five-unit compile/mismatch measurements and exact source-assembly results remain valid. No coverage percentage changes.

Additional direct pinned-source check: `csky_cfft_q15.c` defines `csky_cfft_q15`, and `csky_bitreversal.c` defines `csky_bitreversal_q15`. Both source bytes match the registered pin; the receipt now passes **28 checks**. All six earlier undefined wrapper symbols therefore have available C definitions. This does not establish that compiling those units produces a fully resolved transform object: they may introduce further dependencies, and owner build/link receipts must settle that.
