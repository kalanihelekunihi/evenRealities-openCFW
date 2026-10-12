/* Experimental single-owner compilation of the pinned clock header.
 * Including the three wrappers in one translation unit prevents repeated
 * static tables from clk_priv.h. This file is not in the selected image-B
 * source list until its relocations and native table layout are qualified. */
#include "backup_clock_module_select.c"
#include "backup_clock_frequency.c"
#include "backup_platform_gate.c"

/* The SDK header's one table instance also owns the three original
 * image-B table addresses. Validate these aliases on the C-SKY target. */
__asm__(".globl gx8002_image_b_clock_param_table_1001699c\n"
        "gx8002_image_b_clock_param_table_1001699c = gx_clock_param_table\n"
        ".globl gx8002_image_b_clock_dto_table_10016b3c\n"
        "gx8002_image_b_clock_dto_table_10016b3c = gx_clock_dto_table\n"
        ".globl gx8002_image_b_clock_div_table_10016b40\n"
        "gx8002_image_b_clock_div_table_10016b40 = gx_clock_div_table\n");
