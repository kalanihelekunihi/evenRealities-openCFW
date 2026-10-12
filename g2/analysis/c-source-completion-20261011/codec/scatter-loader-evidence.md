# Codec stage-2 scatter and loader evidence

The pinned NationalChip GX8002 source `third-party/upstream/nationalchip-lvp-kws/arch/soc/grus/link.ld`
(SHA-256 `1dc73b74c4b5962a848693ab857e90d34115489a8a7e499897533ad786ff77be`)
defines separate stage-2 XIP text, SRAM text, SRAM initialized data and BSS
sections. Lines 239–293 place XIP text and read-only data. Lines 295–359
place selected SRAM code and read-only data in `stage2_iram`, reserve a
same-sized DRAM hole, then place initialized data in `stage2_dram`.
The XIP LMA expressions put SRAM text/data after the XIP section and four-byte
stage-2 header. The exact product configuration macros, object list and
producer map remain to be authenticated for these packaged images.

Pinned `arch/soc/grus/spl/spl.c` (SHA-256
`f3690694fff309c0118579baedb860b1d47c6de3cfb227a977242249568bb56b`)
lines 218–254 computes the SRAM text and initialized-data extents and asks
`sflash_readdata` to read their combined length from the NOR image into
`_stage2_sram_start_text_`. It then branches to the stage-2 reset entry.
This source establishes the producer's intended contiguous load contract;
it does not prove that the stock package used this exact configuration or
that the present target replays the same flash and alias behavior.

For native image-B, the retained stage-2 payload is 82,060 bytes from base
`0x10003000`. Its terminal 300 bytes are therefore
`0x10016f60..0x1001708c`, numerically matching the typed initialized-data
range `0x20016f60..0x2001708c` through the IRAM/DRAM address alias. This
explains why the image-B reset body has no separate 300-byte copy loop in
the retained pseudocode. The actual stock stage-1 loader and hardware alias
must still be checked before admitting final image-B startup.

The canonical stock stage-1 images each start with `BINH`, magic
`0x55aa55aa`, version word `0x203`, and a `0x3000` stage-1 size word.
Their stage-2 length words at offset `0x0c` are `0xc800` for A and
`0x1408c` for B, exactly the extracted 51,200- and 82,060-byte stage-2
payloads. This independently ties the native payload extents to the
packaged stage-1 headers. The header words alone do not prove the runtime
flash destination or physical alias semantics.

For image-A, the authenticated package lengths and addresses are XIP
`0x10203004..0x1020be88` (36,484 bytes) and SRAM
`0x10023400..0x10026d7c` (14,716 bytes). The source-only packed XIP
candidate leaves 72 bytes before alignment/veneers/literals. Corrected
resident placement splits code around the exact `0x10025cd0..0x10025d04`
clock records, leaving 104 bytes before those records and 674 bytes between
the following code and the exact 2,200-byte initialized tail. The earlier
monolithic pack overlapped the internal records and is superseded. These
are capacity measurements, not a complete link. Final section
allocation must fit all branch reach, literal pools, section alignment and
the product's loaded segment extents while preserving exact source-owned
data and vector addresses. No unverified extra region is assumed.

The stock image-A stage-1 native first-firmware path is now separately
qualified by `excluded-section-eligibility/stage1-copy-contract.json`.
At `0x10000a9e..0x10000aa0` it reads the four-byte stage-2 XIP length;
at `0x10000aa4..0x10000ab8` it computes the combined SRAM length from
authenticated linker addresses as `0x397c`, invokes the native flash reader
for destination `0x10023400`, then jumps to `0x10023500`. The `BINH`
stage-2 length `0xc800` leaves `0x8e84` (36,484) bytes before SRAM.
This closes the nominal **stock** A copy extent and entry. Alternate
multiboot, flash hardware effects and a custom source image's exact
placement/branch reach remain separate gates.
