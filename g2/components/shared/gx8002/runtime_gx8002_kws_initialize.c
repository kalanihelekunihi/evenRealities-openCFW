/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern void open_cfw_gx8002_kws_flash_load(void);
extern int gx_snpu_init(void);
extern volatile uint32_t open_cfw_gx8002_kws_callback;
int open_cfw_gx8002_kws_initialize(uint32_t callback, uint32_t start_mode)
{
    if (start_mode < 2u) open_cfw_gx8002_kws_flash_load();
    gx_snpu_init();
    open_cfw_gx8002_kws_callback = callback;
    return 0;
}
