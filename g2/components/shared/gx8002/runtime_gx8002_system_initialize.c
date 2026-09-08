/* SPDX-License-Identifier: MIT */
/* Reconstructed startup ordering; MPU/VIC operations use pinned CSI helpers.
 * Matches NationalChip arch/soc/grus/system.c without its conflicting global
 * typedef headers. The external calls require separate source qualification. */
#include <core_ck804.h>
extern void open_cfw_gx8002_clock_initialize(void);
extern int open_cfw_gx8002_start_mode(void);
extern void open_cfw_gx8002_clear_bss(void);
extern void open_cfw_gx8002_board_initialize(void);
extern const unsigned int open_cfw_gx8002_vectors[];

void open_cfw_gx8002_system_initialize(void)
{
    mpu_region_attr_t attr;
    attr.nx = 0;
    attr.ap = AP_BOTH_RW;
    attr.s = 0;
    csi_mpu_config_region(0, 0, REGION_SIZE_4GB, attr, 1);
    csi_mpu_enable();
    open_cfw_gx8002_clock_initialize();
    if (open_cfw_gx8002_start_mode() == 0)
        open_cfw_gx8002_clear_bss();
    open_cfw_gx8002_board_initialize();
    __set_VBR((uint32_t)open_cfw_gx8002_vectors);
    VIC->TSPR = 0xff;
    for (unsigned int i = 0; i < 4; ++i) {
        VIC->IABR[i] = 0;
        VIC->ICPR[i] = 0xffffffff;
    }
    __enable_excp_irq();
}
