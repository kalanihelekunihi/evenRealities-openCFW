/* SPDX-License-Identifier: MIT
 * Image-A wakeup/board bridge and its XIP analog update lower.
 * Native SRAM: 0x10024940 and 0x10025cbc. Native XIP: 0x10203c74.
 */
#include <stdint.h>

extern uint32_t gx8002_resident_flash_initialize_245f0(void);

/* Stock 0x10024940 (gx_pmu_get_wakeup_source) */
uint32_t gx8002_resident_pmu_wakeup_source_24940(void)
{
    volatile uint32_t *const clock =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0000000);
    uint32_t flags = clock[0x34u / 4u];
    if ((flags & 1u) != 0u) return 2u;
    if ((flags & 4u) != 0u) return 3u;
    if ((flags & 8u) != 0u) return 5u;
    if ((flags & 2u) != 0u) return 4u;
    const volatile uint32_t *const pmu =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010000);
    return pmu[0x2cu / 4u] & 1u;
}

void gx8002_resident_analog_config_update_10203c74(void)
{
    volatile uint32_t *const analog =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005000);
    analog[0x40u / 4u] = 0x59u;
    analog[0x44u / 4u] = 0x59u;
    analog[0x48u / 4u] = 0x59u;
    analog[0x4cu / 4u] = 0x59u;
}

/* Stock 0x10025CBC (gx8002_board_initialize) */
void gx8002_resident_board_initialize_25cbc(void)
{
    if (gx8002_resident_pmu_wakeup_source_24940() >= 2u)
        (void)gx8002_resident_flash_initialize_245f0();
    gx8002_resident_analog_config_update_10203c74();
}
