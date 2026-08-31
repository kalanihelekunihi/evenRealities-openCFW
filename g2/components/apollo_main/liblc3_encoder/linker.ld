/* SPDX-License-Identifier: MIT */
/*
 * Build-only section layout for the admitted liblc3 encoder closure.
 * No runtime addresses are assigned here.  A future placement component must
 * resolve the retained imports and all emitted relocations after choosing
 * authenticated Apollo-main storage.
 */
SECTIONS
{
    .text : ALIGN(16)
    {
        *(SORT_BY_NAME(.text.*))
    }

    .rodata : ALIGN(16)
    {
        *(SORT_BY_NAME(.rodata.*))
        *(SORT_BY_NAME(.rodata.cst*))
    }

    .data : ALIGN(8)
    {
        *(SORT_BY_NAME(.data.*))
    }

    /DISCARD/ :
    {
        *(.ARM.exidx*)
        *(.rel.ARM.exidx*)
    }
}
