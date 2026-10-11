/* SPDX-License-Identifier: MIT
 * Direct native package pool registration 0x100061e4. Pool count
 * at 0x200099c8 and eight 12-byte descriptors at 0x2000a19c are
 * runtime product state. Allocation at 0x10006fac is a real lower.
 */
#include <stdint.h>

static const char pool_error_format[] =
    "Too much pkg memory demanded: %d\n";

extern void *gx8002_uart_stage2_pool_allocate_6fac(uint32_t start,
                                                     uint32_t bytes);
extern int32_t gx8002_uart_stage2_launch_61a4(const char *format, ...);

void gx8002_uart_stage2_configure_61e4(uint32_t start, uint32_t bytes)
{
    volatile uint32_t *const count_word =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x200099c8);
    volatile uint32_t *const descriptors =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2000a19c);
    const uint32_t count = *count_word;
    if ((int32_t)count > 0) {
        for (uint32_t i = 0; i < count; ++i) {
            if (descriptors[i * 3u + 1u] == start) return;
        }
        if (count == 8u) return;
    } else if (count != 0) {
        return;
    }
    void *const allocation = gx8002_uart_stage2_pool_allocate_6fac(
        start, bytes);
    descriptors[count * 3u] = (uint32_t)(uintptr_t)allocation;
    if (allocation == 0)
        gx8002_uart_stage2_launch_61a4(pool_error_format, bytes);
    descriptors[count * 3u + 1u] = start;
    descriptors[count * 3u + 2u] = bytes;
    *count_word = count + 1u;
}
