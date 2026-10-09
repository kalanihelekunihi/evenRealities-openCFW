# GNU 14.2.1 exact three-function comparator

Arm GNU Toolchain 14.2.Rel1, GCC 14.2.1 20241119 (Build arm-14.52), compiles
unchanged pinned PDL to **exact complete section bytes for all three controls**:

| Function | Stock address | Complete section | Difference | Relocations |
| --- | --- | --- | --- | --- |
| Cy_MSCLP_Configure | 0x8FD0 | 424 bytes | zero | none |
| Cy_MSCLP_Capture | 0x8FA0 | 48 bytes | zero | none |
| Cy_MSCLP_ConfigureScan | 0x9178 | 160 bytes | zero | none |

This resolves the prior 24-byte Configure loop-layout mismatch under the
recorded comparator environment. It supports this exact public-source/header
and GNU14.2.1 build as a three-function reproduction, not a unique producing
compiler/source checkout or whole-image equality. No bytes or source were
patched to obtain the match. Earlier 10.3–13.3 receipts remain unchanged.

Official listing and checksum discovery are recorded in
`source-discovery-parallel-2026-10-09/ARM-14.2-OFFICIAL-ACQUISITION.md`.
Archive SHA-256
`62a63b981fe391a9cbad7ef51b17e49aeaa3e7b0d029b36ca1e9c3b2a9b78823`
matches the official published checksum before extraction. Despite its
`.sha256asc` filename the acquired checksum is plain text; no signature
verification is claimed. Exact public package URL/compiler hash are in
`acquisition.json`. No bot challenge was solved or bypassed.

The source remains `cy_msclp.c` SHA-256
`2613ec6fee3ac2ca6d8a42e483bb671f9ed63a58045b125ee6fe11f6f2d60f07`,
PDL pin `35f1714623cfea682d5e285af80d50416b4c7bbc`. Flags remain
`-mcpu=cortex-m0plus -mthumb -Og -ffreestanding -fno-builtin
-DCY8C4046FNI_T412 -ffunction-sections`. All 27 consumed noncompiler inputs
match the prior13.3 receipt. Configure preprocesses to the identical normalized
definition SHA-256 used by the older matrix. Thus this test changes the
compiler/tool headers while preserving the observed public function text and
noncompiler source environment.

`results.json` records compiler/version/archive hashes, flags/includes,
consumed-file hashes, complete section sizes/hashes/equality, absent relocations
and retained output hashes. Object, assembly, preprocessed input and dependencies
are retained in locally ignored isolated outputs. `matrix.py` is the execution
recipe. It uses approved Docker sandbox escalation, the same digest-pinned
Ubuntu linux/amd64 runtime, no network, no capabilities, no-new-privileges,
read-only tool/source/header mounts and only a task output writable mount.

Independent review remains pending. This changes local Configure attribution
evidence from behavioral-only to an exact compiled-source comparator; it adds
no newly recovered function count, original-instruction execution, physical
claim, firmware patch, campaign admission or gate pass. Further compiler sweeps
are unnecessary without a new specific question; broader touch reconstruction
needs independent function/configuration coverage and whole-image accounting.
