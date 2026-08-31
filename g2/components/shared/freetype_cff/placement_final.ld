/*
 * SPDX-License-Identifier: MIT
 *
 * Final CFF placement in the authenticated append interval of the canonical
 * Apollo-main component.  The enclosing finalizer must bind every retained
 * import and verify the resulting image before this layout has any authority.
 */

SECTIONS
{
  .placement_prefix 0x007ECA44 :
  {
    BYTE(0)
    . = ALIGN(16);
  }

  .text :
  {
    *(.text)
    *(.text.*)
  }

  .arm_exidx :
  {
    *(.ARM.exidx*)
    *(.ARM.extab*)
  }

  .rodata :
  {
    *(.rodata)
    *(.rodata.*)
  }

  .data :
  {
    *(.data)
    *(.data.*)
  }

  .bss (NOLOAD) :
  {
    *(.bss)
    *(.bss.*)
    *(COMMON)
  }

  ASSERT(. <= 0x007FE000, "CFF placement overlaps protected update record")

  /DISCARD/ :
  {
    *(.comment)
    *(.note.GNU-stack)
    *(.llvm_addrsig)
    *(.ARM.attributes)
  }
}
