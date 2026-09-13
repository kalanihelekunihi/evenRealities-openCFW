/* SPDX-License-Identifier: MIT */
#include <stdint.h>
/* Channel enum: stereo=0, left=1, right=2, mono=3. Stock also accepts
 * other unsigned values, selecting left/left without mixing. Encode the
 * observed channel mapping as logic, without a stock table dependency. */
int open_cfw_gx8002_aout_set_channel(int handle, unsigned int channel)
{
    (void)handle;
    uint32_t left=channel==2;
    uint32_t right=channel==0 || channel==2 || channel==3;
    uint32_t mixed=channel==3;
    volatile uint32_t *reg=(volatile uint32_t *)0xa0b00014u;
    *reg=(*reg&~0xf00u)|(left<<8);
    *reg=(*reg&~0xf000u)|(right<<12);
    *reg=(*reg&~1u)|mixed;
    return 0;
}
