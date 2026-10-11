/* SPDX-License-Identifier: MIT
 * Native XIP KWS initialization/teardown 0x10206d90/0x10206dac.
 * Flash loading and SNPU lifecycle remain genuine external lower contracts.
 */
#include <stdint.h>

extern void gx8002_xip_kws_flash_load_10206cb0(void);
extern void gx8002_xip_snpu_initialize_10205cf4(void);
extern void gx8002_xip_snpu_exit_10205d40(void);

static volatile uint32_t *const kws_callback_slot =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027b50);

uint32_t gx8002_xip_kws_initialize_10206d90(
    uint32_t (*callback)(uint32_t, uint32_t, uint32_t), uint32_t source)
{
    if (source < 2u) gx8002_xip_kws_flash_load_10206cb0();
    gx8002_xip_snpu_initialize_10205cf4();
    *kws_callback_slot = (uint32_t)(uintptr_t)callback;
    return 0u;
}

void gx8002_xip_kws_done_10206dac(void)
{
    gx8002_xip_snpu_exit_10205d40();
    *kws_callback_slot = 0u;
}
