/* Partial C-SKY loaded image-B placement probe. No vector/reset or CRT
 * normal-copy image is emitted here, so this is not a bootable ELF. */
SECTIONS
{
  .text 0x10003100 : { *(.text*) }
  .rodata : { *(.rodata*) }

  .clock_param 0x1001699c : { KEEP(*(.data.gx_clock_param_table)) }
  .clock_dto 0x10016b3c : { KEEP(*(.data.gx_clock_dto_table)) }
  .clock_div 0x10016b40 : { KEEP(*(.data.gx_clock_div_table)) }

  .gsensor_state 0x20016f60 : {
    KEEP(*(.data.gx8002_image_b_gsensor_workstate_20016f60))
  }
  .imcra_profile 0x20016fb8 : {
    KEEP(*(.data.gx8002_image_b_imcra_cfg_words_20016fb8))
  }
  .data : { *(.data*) }
  .bss (NOLOAD) : { *(.bss*) *(COMMON) }

  .image_b_retained.energy 0x2002d79c (NOLOAD) : {
    KEEP(*(.image_b_retained.energy))
  }
  .image_b_retained.ring 0x2002d7a0 (NOLOAD) : {
    KEEP(*(.image_b_retained.ring))
  }
  .image_b_retained.dsp_operations 0x2002d7a4 (NOLOAD) : {
    KEEP(*(.image_b_retained.dsp_operations))
  }
  .image_b_retained.imcra_setting 0x2002d7b4 (NOLOAD) : {
    KEEP(*(.image_b_retained.imcra_setting))
  }
}
PROVIDE(gx8002_image_b_bss_start = 0x20017090);
PROVIDE(gx8002_image_b_bss_end = 0x2002d79c);
ASSERT(ADDR(.rodata) + SIZEOF(.rodata) <= 0x1001699c,
       "source text/rodata over clock table");
ASSERT(SIZEOF(.clock_param) == 0x1a0, "clock param extent");
ASSERT(SIZEOF(.clock_dto) == 3, "clock DTO extent");
ASSERT(SIZEOF(.clock_div) == 0x44, "clock div extent");
ASSERT(SIZEOF(.gsensor_state) == 4, "gsensor state extent");
ASSERT(SIZEOF(.imcra_profile) == 0x54, "IMCRA profile extent");
ASSERT(SIZEOF(.data) == 0, "unexpected runtime initialized data");
ASSERT(SIZEOF(.image_b_retained.energy) == 4, "energy cell extent");
ASSERT(SIZEOF(.image_b_retained.ring) == 4, "ring cell extent");
ASSERT(SIZEOF(.image_b_retained.dsp_operations) == 16,
       "DSP callback table extent");
ASSERT(SIZEOF(.image_b_retained.imcra_setting) == 4,
       "IMCRA setting cell extent");
