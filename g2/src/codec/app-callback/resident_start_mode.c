/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10024984..0x100249a1 native start-mode test.
 * The second PMU register read is retained as a volatile side effect.
 */
#include <stdint.h>

extern uint32_t gx8002_resident_pmu_wakeup_source_24940(void);

/* Stock 0x10024984 (gx8002_start_mode) */
uint32_t gx8002_resident_start_mode_24984(void)
{
    uint32_t source = gx8002_resident_pmu_wakeup_source_24940();
    if (source - 2u >= 4u) return 0u;
    const volatile uint32_t *const pmu =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010000);
    uint32_t mode = pmu[0x58u / 4u] & 1u;
    (void)pmu[0x5cu / 4u];
    return mode;
}
