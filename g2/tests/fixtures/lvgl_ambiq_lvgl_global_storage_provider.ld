/* SPDX-License-Identifier: MIT */
SECTIONS
{
    . = 0x2006F548;
    .open_cfw_lv_global (NOLOAD) :
    {
        KEEP(*(.bss.lv_global))
    }

    ASSERT(ADDR(.open_cfw_lv_global) == 0x2006F548,
           "lv_global placement changed")
    ASSERT(SIZEOF(.open_cfw_lv_global) == 0x1EC,
           "lv_global extent changed")
}
