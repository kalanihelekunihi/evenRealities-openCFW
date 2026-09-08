/* SPDX-License-Identifier: MIT */
/* One volatile state read; the SDK defines IDLE=0, BUSY=1 and STALL=2. */
#include <stdint.h>
#include <driver/gx_snpu.h>
_Static_assert(sizeof(GX_SNPU_STATE) == sizeof(uint32_t), "GRUS state ABI");
extern volatile GX_SNPU_STATE open_cfw_gx8002_snpu_state;
GX_SNPU_STATE open_cfw_gx8002_snpu_get_state(void)
{
    return open_cfw_gx8002_snpu_state;
}
