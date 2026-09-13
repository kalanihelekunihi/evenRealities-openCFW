/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern void open_cfw_gx8002_dcache_clean_range(uint32_t, uint32_t);
/* Stock e3f8: config must be readable; handle is unused. A bad second
 * buffer is rejected after the first buffer has already been programmed.
 * Preserve the configuration rereads across cache-clean calls. */
int open_cfw_gx8002_aout_config_buffer(int handle, const volatile uint32_t *config)
{
    (void)handle;
    uint32_t address=config[0];
    if (!address || (address&15u)) return -1;
    volatile uint32_t *sdc=(volatile uint32_t *)0xa0b80000u;
    sdc[1]=address+0xe0000000u;
    open_cfw_gx8002_dcache_clean_range(address,config[2]);
    address=config[1];
    if (address) {
        if (address&15u) return -1;
        sdc[2]=address+0xe0000000u;
        open_cfw_gx8002_dcache_clean_range(address,config[2]);
    }
    sdc[3]=config[2];
    return 0;
}
