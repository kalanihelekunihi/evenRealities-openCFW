/* SPDX-License-Identifier: MIT
 * Native XIP 0x10207680..0x102076b5: cold/WDT clears the 0x90-byte
 * power state; warm wakeup iterates its registered callback pairs.
 * The table/count addresses and return values are from stock instructions.
 */
#include <stdint.h>

extern uint32_t gx8002_resident_pmu_wakeup_source_24940(void);
extern void gx8002_xip_memset_102099cc(void *, uint32_t, uint32_t);

typedef void (*gx8002_power_callback)(uint32_t);

uint32_t gx8002_xip_power_initialize_10207680(void)
{
    if (gx8002_resident_pmu_wakeup_source_24940() < 2u) {
        gx8002_xip_memset_102099cc(
            (void *)(uintptr_t)UINT32_C(0x2002dfbc), 0u, 0x90u);
        return 1u;
    }
    volatile const uint32_t *const count =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x2002dfc8);
    volatile const uint32_t *const callbacks =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x2002e00c);
    for (uint32_t index = 0; index < *count; ++index) {
        uint32_t raw = callbacks[index * 2u];
        uint32_t argument = callbacks[index * 2u + 1u];
        ((gx8002_power_callback)(uintptr_t)raw)(argument);
    }
    return 0u;
}
