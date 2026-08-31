/* SPDX-License-Identifier: MIT */
/*
 * Qualification-only layout for the specialized encoder's logically
 * immutable pointer tables.  Final placement must assign addresses and apply
 * every relocation before emitting these bytes as read-only XIP data.
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

    /* llvm-objcopy clears SHF_WRITE only after the analyzer proves closure. */
    .lc3_table_rodata : ALIGN(8)
    {
        *(.data.lc3_band_lim)
        *(.data.lc3_fft_twiddles_bf2)
        *(.data.lc3_fft_twiddles_bf3)
        *(.data.lc3_mdct_rot)
        *(.data.lc3_mdct_win)
    }

    .unexpected_writable : ALIGN(8)
    {
        *(.data)
        *(.data.*)
    }

    /DISCARD/ :
    {
        *(.ARM.exidx*)
        *(.rel.ARM.exidx*)
    }
}

ASSERT(SIZEOF(.lc3_table_rodata) == 404,
       "specialized LC3 pointer-table size changed")
ASSERT(SIZEOF(.unexpected_writable) == 0,
       "specialized LC3 retained unexpected writable data")
