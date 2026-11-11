/* SPDX-License-Identifier: MIT
 * Stock 0x432958..0x43297a (fpu_enable_432958; IAR __iar_init_vfp): startup
 * CPACR/FPSCR initialization. CP10/CP11 full-access mask and the FPSCR value
 * 0x02040000 (DN, LTPSIZE = 4) were recovered from the image.
 */
#include <stdint.h>

#include "apollo510.h"

void opencfw_boot_fpu_init(void)
{
    SCB->CPACR |= 0xFu << 20;
    __DSB();
    __ISB();
    __set_FPSCR(0x02040000u);
}
