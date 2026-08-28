# G2 bootloader address-identified retained-value wrapper source closure

Status: software implemented and production-routed; physical validation blocked.

The complete eight-byte entry `[0x004161C6,0x004161CE)` has SHA-256
`8bca4189bfd5992611480a59010d921df4ced8b191396b455f3223c270f19f66`
and authenticated direct callers at `0x0042E286` and `0x0042E296`. It forwards
the exact 32-bit result of the retained getter at `0x00418B4E`. The
address-derived name deliberately avoids assigning unsupported meaning to the
getter or its SRAM value. Host tests pin zero, one, an arbitrary word, and the
full unsigned range endpoint, with exactly one retained call each.

`runtime_value_4161c6.c` is a 425-byte MIT clean-room
implementation with SHA-256
`21e70612f2f997db633a6be6b7dcdac8e3ce428a72edd94de79f3334b1c931e4`.
Apple clang emits a four-byte leaf at overlay offset 3,306/runtime
`0x00435162`. Its unrelocated SHA-256 is
`90a54a1f68a806a1795bd044856908235426b3c0f67be605fb94d3d5344a747f`
and its relocated SHA-256 is
`8c0c36947cd33a1402603053d37a41296bd577db49bb1fa6a22fd0ee38248de8`.
One strict `R_ARM_THM_JUMP24` relocation at offset zero binds the retained
getter. The stock entry is replaced exactly by `1ef0ccbf` and two Thumb NOPs.
Homebrew clang 22.1.8 emits the same unrelocated leaf at profile offset 3,296;
its relocated SHA-256 is
`cc6890849d82d2903cbbceb1ad71d2ffff0a14fbb890041f113da0a3758cbb01`.

This extends the runtime tranche to twenty entries at
`[0x00415844,0x004161CE)`: 2,406 exact stock bytes, 116 authenticated caller
edges, 2,198 canonical compiled Thumb bytes, and 35 strict relocations. The
canonical overlay is 3,310 bytes with SHA-256
`e37a8aae91a6155c96c34b684067cb1892f4797b37579978da402f661361cee3`.
The 151,910-byte provider hashes to
`2cad937b43cebd65fead69e674c42a3a5fb5b875b01ea67210247685821427f5`,
has CRC-32C/MSB `0x50CFD1B3`, and accounts for 3,303 source, 3,858 patch,
eight alignment, and 144,741 retained authenticated bytes. It ends at
`0x00435166`, leaving 11,930 bytes before Apollo main. The Linux overlay is
3,300 bytes with SHA-256
`879c34a40f8e36aaeed354958ea2ff7f73dc1d0c17abafdfa98b2d0137ea4d74`;
its 151,900-byte provider hashes to
`e13616ae5ee03777b74505f7eeb78b21af25bb17852e8420f74b9a2b307a22e3`.

The canonical unsigned package is 4,733,488 bytes with SHA-256
`dff6d17a4883b7464492a1db3b14421fb4a7d17cf2f36d0cea77e4d6163561db`.
Its 4,344,753-byte flash plan hashes to
`288d074239068ddd3851e05008fe25bee64fbb2cc396e432659fe27546bca871`
and records 6,258 placed, two unresolved, five container-only, and six
protected regions. The independent Linux package is 4,509,488 bytes with
SHA-256
`07e2ee4d91414fcc2c5bd5f3db39f0cd8c035b8befec2dd18d7dc38e68e7edc3`;
its 2,312,614-byte plan hashes to
`ffb862102820a09dbf3973254488c8b7914f01ecdbace5d9ae7d6e558ba29411`
and records 3,325 placed regions plus the same two unresolved boundaries.

This checkpoint is superseded by
`g2-bootloader-runtime-call-4161ce-source-closure.md`, which closes the next
complete callable body. No image was signed, installed, flashed, reset, or booted.
Authorized physical validation is blocked because the right temple is
nonresponsive, the left must remain stock, and no responsive authorized unit
or equivalent trace is available. Consequently this closure makes no live
getter-value, caller-path, or concurrency claim and does not declare
bootloader or firmware-wide functional completeness.
