/* SPDX-License-Identifier: MIT
 * Direct native UART completion callback 0x10002f98 and VIC restore
 * helper 0x100030b4. The former invokes the callback saved at +0x58
 * with port and the argument at +0x5c, after cache range command 10.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_cache_range_3310(uint32_t address,
                                                  int32_t length);

void gx8002_uart_stage2_irq_handler_2f98(volatile uint32_t *descriptor)
{
    descriptor[0x68 / 4] = UINT32_MAX;
    gx8002_uart_stage2_cache_range_3310(descriptor[0x60 / 4],
        (int32_t)descriptor[0x64 / 4]);
    uintptr_t target = (uintptr_t)descriptor[0x58 / 4];
    void (*complete)(uint32_t, uint32_t) =
        (void (*)(uint32_t, uint32_t))target;
    complete(descriptor[0], descriptor[0x5c / 4]);
}

void gx8002_uart_stage2_vic_restore_30b4(void)
{
    volatile uint32_t *const saved =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20009844);
    volatile uint32_t *const vic =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000e100);
    vic[0] = saved[0];
    vic[1] = saved[1];
}
