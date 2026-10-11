/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x1002475c..0x100247ab, native callback/retry loop.
 * The callback slot and probe flag are runtime state at authenticated SRAM
 * addresses; no success value or callback is synthesized here.
 */
#include <stdint.h>

extern uint64_t gx8002_resident_clock_time_us_2585c(void);

typedef int32_t (*gx8002_probe_callback)(
    uint32_t, uint32_t, uint32_t, uint32_t);

int32_t gx8002_resident_flash_probe_2475c(
    uint32_t arg0, uint32_t arg1, uint32_t arg2, uint32_t arg3)
{
    uint64_t start = gx8002_resident_clock_time_us_2585c();
    volatile uint8_t *const probe_flag =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x20026ff4);
    const volatile uint32_t *const callback_slot =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x20026504);
    do {
        if (*probe_flag < 2u) {
            gx8002_probe_callback callback =
                (gx8002_probe_callback)(uintptr_t)(*callback_slot);
            int32_t result = callback(arg0, arg1, arg2, arg3);
            if (result != 0) {
                *probe_flag = 1u;
                return result;
            }
        }
    } while (gx8002_resident_clock_time_us_2585c() - start <=
             UINT64_C(0x4c4b3f));
    return 0;
}
