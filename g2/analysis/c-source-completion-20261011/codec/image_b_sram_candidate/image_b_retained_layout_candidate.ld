/* Partial, source-backed SRAM placement for loaded image B.
 * This script is for a relocatable layout audit. It is not a bootable
 * firmware linker script: vector/reset, normal-copy data, and two ambient
 * callable contracts remain separate work. */
SECTIONS
{
  .text 0 : { *(.text*) }
  .rodata : { *(.rodata*) }
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

/* Native CRT at 0x10003128 zeros [start,end). These are exact stock
 * addresses, independent of the custom source output .bss section. */
PROVIDE(gx8002_image_b_bss_start = 0x20017090);
PROVIDE(gx8002_image_b_bss_end = 0x2002d79c);

ASSERT(SIZEOF(.image_b_retained.energy) == 4, "energy cell extent");
ASSERT(SIZEOF(.image_b_retained.ring) == 4, "ring cell extent");
ASSERT(SIZEOF(.image_b_retained.dsp_operations) == 16,
       "DSP callback table extent");
ASSERT(SIZEOF(.image_b_retained.imcra_setting) == 4,
       "IMCRA setting cell extent");
