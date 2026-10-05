# Codec upstream held-out comparison

## Finding

The bounded held-out target was the C-SKY SDK routine `gx_i2s_set_five_wire_mode`, supplied as a compiled ELF section in NationalChip `lvp_kws` commit `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`. The 830-byte `.text.gx_i2s_set_five_wire_mode` section (SHA-256 `1ea213d3973418cb1210fe2113b89b5dca1de001779cd0533217c9c0f9c0bb81`) has an associated `.rela` section of 132 bytes (11 relocation entries). An exact raw byte search over the entire authenticated `firmware_codec.bin` found zero occurrences. This yields no firmware address, no addressable byte interval, and no newly verified range. The no-hit result does not establish that the implementation is absent: relocations, compiler/build variation, or a different implementation can change bytes.

The selected symbol does not appear in `g2/symbols/codec.tsv`. The relevant source checkout contains `include/driver/gx_i2s/gx_i2s_v2.h` but not the driver implementation C file. The header defines `gx_i2s_set_five_wire_mode(GX_I2S_FIVE_WIRE_MODE mode)`, enumerates 12 five-wire modes, and documents `0` success / `-1` failure. This is useful interface evidence for future pseudocode review, not proof that stock firmware calls this API or that the compiled SDK section is its exact stock implementation.

## Scope, identities, and limits

- Locked payload: `g2/blobs/official/g2-2.2.6.10/firmware_codec.bin`, 326,092 bytes, SHA-256 `b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0`.
- SDK object: `third-party/upstream/nationalchip-lvp-kws/drivers_lib/i2s/v2.0/i2s.o`, SHA-256 `97706af775b19c9f71715545ba0ee5df924fb8b90bd0b59e21c786cdf945902c`.
- Object metadata says 32-bit little-endian C-SKY relocatable ELF; candidate section `.text.gx_i2s_set_five_wire_mode`, size 830, SHA-256 above; relocation section `.rela.text.gx_i2s_set_five_wire_mode`, 132 bytes / 11 entries.
- The scan compared the section's stored bytes directly against every possible byte offset in the full authenticated codec payload. Because the section has relocations, this scan is only an exact stored-byte test; it does not normalize relocations or model linker/compiler transformations.
- Existing baseline remains the consolidated reference count: 102 matching eligible SDK sections, 68 symbols, 5,374 bytes from 151 eligible sections (`g2/docs/reference/toolchains.md:242-244`). This batch adds **0** ranges and does not revise that denominator or prior count.

## Previously matched controls; excluded from new counts

As a check against repeating old UART results, raw searches of the same authenticated payload reproduced hits already listed in `g2/symbols/codec.tsv`: `dw_uart_putc` 20 bytes at package offset `0x0C7D8`; `dw_uart_getc` 22 bytes at `0x02F1E` and `0x0C7EC`; `dw_uart_isr` 230 bytes at `0x0C804`; `dw_uart_get_fifo_depth` 102 bytes at `0x0C8EC`; and `dw_uart_dma_get_burst_size` 114 bytes at `0x0C5DC`. These are all prior matches and contribute zero new bytes here.

## Source and licensing status

The repo-level `third-party/upstream/nationalchip-lvp-kws/LICENSE` is MIT, and the checked-out LVP/KWS repository is pinned to the commit above. That licenses the checked-out project subject to its notice/terms; it does not establish source availability or byte identity for every firmware module. In particular, the I2S implementation source is absent here while its precompiled object is present. The separate `nationalchip-gxdnn` checkout is pinned at `0637b47c8fa0031f8f5651a903cd7d14716382fd`; `third-party/README.md` records “no licence declared,” so no licensing claim is made for its archives. No archive or licensed material was downloaded.

## Reproduction evidence

The target SHA was recomputed locally. The candidate object section and relocation metadata were read from the ELF section table, and exact byte search was performed against the payload. Prior-match controls were matched against `codec.tsv`. No decompilation, build, or firmware modification was done.
