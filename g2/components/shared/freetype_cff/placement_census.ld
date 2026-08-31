/*
 * SPDX-License-Identifier: MIT
 *
 * Relocatable-link layout for the admitted FreeType 2.9.1 CFF translation
 * unit and its openCFW policy adapter.  Addresses deliberately remain zero:
 * this file measures the loadable sections and preserves every relocation;
 * it does not grant production placement.
 */

SECTIONS
{
  .text 0 :
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

  /DISCARD/ :
  {
    *(.comment)
    *(.note.GNU-stack)
    *(.llvm_addrsig)
  }
}
