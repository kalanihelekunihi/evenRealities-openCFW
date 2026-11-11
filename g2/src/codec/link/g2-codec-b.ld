/*
 * openCFW G2 codec image B (GX8002 SRAM backup image) linker script -- Wave 13.
 *
 * Evidence:
 * - Stock corpus RUN.json (firmware_codec.bin 2.2.6.10): image_b_sram base
 *   0x10003000, 82060 B -> [0x10003000,0x1001708C); memory-map.md: entry 0x10003100
 *   ("Proven"). Previous script modelled UART stage1 (0x10000000/0x10000100); the
 *   payload sources are image B (gx8002_image_b_vectors_10003000, _reset_10003100).
 * - Stock CRT 0x10003128 clears 0x20017090..0x2002d79c (backup_crt_clear_bss.c);
 *   retained cells 0x2002d79c..0x2002d7b8 (backup_runtime_retained_slots.c) are
 *   pinned NOLOAD at those addresses. Linker .bss is confined to the stock clear span.
 * - Image upper bound: GX8002 datasheet 208 KB SRAM -> 0x10034000.
 *   W14 evidence: third-party/upstream/nationalchip-lvp-kws/arch/soc/grus/link.ld places a ".dummy_for_stage2_sram_text_place_hold"
 *   of SIZEOF(.stage2_sram_text) in stage2_dram, and soc_config.h gives IRAM 0x1000xxxx
 *   and DRAM 0x2000xxxx equal sizes: one SRAM, two bus views. So stock image end
 *   0x1001708C == bss start 0x20017090 is the same address.
 * - W15: image end is fixed to the stock bound. -Os profiles plus printf float/exp disabled
 *   (stock evidence in backup_runtime_printf.c) end the image at 0x10016cd8 <= 0x1001708C;
 *   enforced by the ASSERT below.
 */
ENTRY(gx8002_image_b_reset_10003100)

MEMORY
{
  SPL  (rwx) : ORIGIN = 0x10000000, LENGTH = 0x00003000
  SPLDATA (rw) : ORIGIN = 0x20001720, LENGTH = 0x000018dc
  IRAM (rwx) : ORIGIN = 0x10003000, LENGTH = 0x00031000
  BSS  (rw)  : ORIGIN = 0x20017090, LENGTH = 0x0001670c
  RET  (rw)  : ORIGIN = 0x2002d79c, LENGTH = 0x0000001c
}

SECTIONS
{
  /* BINH B's 0x3000-byte stage-1 block is loaded before image B SRAM.
     Keep its source units in their own relocatable: their -Os profile emits
     shared .text/.data sections, which a merged stage-2 object cannot sort. */
  .spl.vectors 0x10000000 : { KEEP(*(.spl.vectors)) } > SPL
  .spl.reset 0x10000100 : { KEEP(*(.spl.reset)) } > SPL
  .spl.default 0x10000130 : { KEEP(*(.spl.default)) } > SPL
  .spl.text : { *g2-codec-b-stage1.o(.text .text.*) } > SPL
  ASSERT(SIZEOF(.spl.vectors) == 0x100 &&
         gx8002_image_b_stage1_reset_10000100 == 0x10000100 &&
         gx8002_image_b_stage1_default_10000130 == 0x10000130,
         "BINH B stage-1 vectors and entries changed")
  ASSERT(ADDR(.spl.text) + SIZEOF(.spl.text) <= 0x10001720,
         "BINH B stage-1 code overlaps initialized data")
  .spl.data 0x20001720 : AT(0x10001720) {
    KEEP(*(.stage1.boot_info))
    KEEP(*(.stage1.transfer_modes))
    KEEP(*(.stage1.uart_baud))
    KEEP(*(.stage1.flash_jedec))
    *g2-codec-b-stage1.o(.data .data.* .rodata .rodata.*)
  } > SPLDATA
  ASSERT(LOADADDR(.spl.data) + SIZEOF(.spl.data) <= 0x10003000,
         "BINH B stage-1 data exceeds the boot block")

  .vectors 0x10003000 : { KEEP(*(.vectors.image_b)) } > IRAM
  .text 0x10003100 : {
    KEEP(*(.text.image_b_reset))
    *(.text .text.*)
    *(.image_b_late_audio)
    *(.rodata .rodata.*)
    . = ALIGN(4);
  } > IRAM
  ASSERT(gx8002_image_b_reset_10003100 == 0x10003100, "image B reset must be at stock 0x10003100")

  .data : ALIGN(4) { __data_start = .; *(.data .data.*) . = ALIGN(4); __data_end = .; } > IRAM

  .bss (NOLOAD) : ALIGN(4) {
    __bss_start = .;
    *(.bss .bss.* COMMON)
    *(.opencfw.abs.bss_start .opencfw.abs.bss_end)
    . = ALIGN(4);
    __bss_end = .;
  } > BSS

  .retained 0x2002d79c (NOLOAD) : {
    KEEP(*(.image_b_retained.energy))
    KEEP(*(.image_b_retained.ring))
    KEEP(*(.image_b_retained.dsp_operations))
    KEEP(*(.image_b_retained.imcra_setting))
  } > RET
}

/* W14: overlap measure (positive = bytes of image overlapping the stock bss alias). */
__codecb_image_end = LOADADDR(.data) + SIZEOF(.data);
__codecb_alias_overlap = __codecb_image_end - 0x1001708C;
ASSERT(__codecb_image_end <= 0x1001708C, "codec-b image overlaps stock CRT bss alias 0x20017090")
