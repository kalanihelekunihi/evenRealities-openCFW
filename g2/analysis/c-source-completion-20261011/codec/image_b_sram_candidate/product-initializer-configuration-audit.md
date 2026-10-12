# Image-B product initializer and runtime configuration audit

The native `0x1000b800..0x1000b8e6` product initializer is already selected
as `backup_denoise_beamforming_init.c`. It constructs angles 35/45/55, copies
four heap operation pointers through `0x1000deb4`, calls the beamforming
create and angle entries, allocates the 2048-byte microphone buffer, computes
the IMCRA size and allocates it, then calls `0x1000d1fc`. All success and
three failure branches are expressed in that C body. The child
`0x1000d1fc` is also selected as `backup_imcra_layout.c`: it writes the
13 source-owned work-region pointers in native order. This is source
attribution, not whole product execution or physical transport proof.

The loaded-stage CRT copies initialized data to `0x20016f60..0x2001708c`
and clears `0x20017090..0x2002d79c`. The 21 typed IMCRA setting words at
`0x20016fb8..0x20017008` are already selected in
`backup_initialized_runtime_data.c`, with their stock 84-byte SHA-256
`f99f330ad9cfd2d7a23ce8b9841877ef452c6515387b2a2f38eaf4813f48889d`.
The allocator/free operation table at `0x2002d7a4..0x2002d7b0` is written
by `0x1000deb4` from source-owned callback addresses. Its location is beyond
the stock CRT-cleared end; a final source linker must allocate/relocate that
runtime object and prove all consumers use the new symbol. The experimental
archive retains it as a typed import pending that placement.

The IMCRA control word at `0x2002d7b4` is one word after the operation table.
The native image-B disassembly contains its literal read at `0x1000e7c6`;
the available image-B literal crosswalk shows no direct literal-address
writer. It also lies beyond the stock copied and CRT-cleared ranges. Thus
its initial or external runtime value is **not** established by the image-B
initializer or the typed 21-word profile. The selected constructor keeps a
genuine `gx8002_image_b_imcra_setting_2002d7b4` import; assigning zero or
borrowing an unrelated setting would invent product behavior. An indirect
writer or loaded-stage/other-image contract still needs attribution. The
constructor passes the word to `0x1000ea74`, which stores it at offset
`+0x10` in IMCRA substate A, so it is a live state value.

The QEMU active-product oracle installs the authenticated `0x1000d1fc`
region arithmetic directly in the fixture because its isolated native
logger transport is not initialized. It does not replace the selected
firmware C body. The final corrected 226-unit receipt is
`build-angle-geometry-orientation-round/receipt.json`; angle 10/10 and
active-process 9/9 finite comparisons pass. A separate native/source oracle
also compares all 12,336 product angle-table bytes directly, with identical
SHA-256 `dc9f9efea3c031390778627302d1942d9887ed0b29e6f38c40a5822995e44b0f`.
The same finite active fixture also has an exact 4,096-byte caller-output
comparison in `native-oracle-run/active-product-output-byte-receipt.json`.
The three whole GSC core imports and six
data/ambient/layout imports remain genuine, and the image's source/data/
final-layout completion flags remain false.

## Exact remaining link contracts

The previous coherent 226-unit archive had nine unresolved names. The
subsequent 227-unit `build-gsc-angle-create-admission-round` binds the complete
angle and create C bodies and leaves seven contracts. The further 228-unit
`build-gsc-process-ram-binding-round` binds native GSC process
`gx8002_image_b_beamforming_process_core_1000d46c`, leaving eight genuine
data, ambient, and placement contracts including the two process RAM words.
Angle has ten
whole-call finite fixtures, create has two, and process has ten active fixtures
plus one exact 4,096-byte caller-output comparison. Full input/failure/FPR
qualification remains open. In particular, native `0x1000dea0` forwards four
register arguments **and a fifth stack word** to process core `0x1000d46c`.
The experimental C composition takes four apparent entry arguments plus two
explicit runtime-RAM state pointers and returns void. Its selected entry
preserves the five-argument native call shape. The full direct process
disassembly does not read the fifth stack word; the identified application
caller overwrites R0 immediately after return. The admitted entry references
two named RAM symbols whose final placement and initialization remain open.
The two process words are adjacent to the operation table: energy first-use
at `0x2002d79c` and ring counter at `0x2002d7a0`, followed by the four
callback words at `0x2002d7a4..0x2002d7b0`. All lie outside the CRT-cleared
range ending at `0x2002d79c` exclusive. Native instruction literals identify
both process reads. The five-argument ABI binding references these words
through linker-owned shared/noinit RAM, preserving their external
initialization contract.

The other six names are `gx8002_image_b_bss_start`,
`gx8002_image_b_bss_end`, `gx8002_image_b_dsp_config_2002d7a4`,
`gx8002_image_b_imcra_setting_2002d7b4`,
`gx8002_image_b_native_word_at_zero_1000ada6`, and
`gx8002_image_b_uart_dma_ambient_direction_100040e8`. The first two are
final linker symbols. The operation table has source-written values but
still needs coherent RAM placement. The IMCRA setting is a live external
control word. The zero-address and UART direction contracts preserve
native ambient memory/register behavior rather than substituting a value.
