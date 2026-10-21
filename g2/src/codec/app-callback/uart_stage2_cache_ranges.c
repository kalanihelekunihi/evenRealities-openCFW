/* SPDX-License-Identifier: MIT
 * Stage-2 cache line operations at 0x100031d8, 0x10003274,
 * and 0x10003310. Each native body writes one command per 16-byte
 * covered line to E000F004. Its 128-byte unroll is a scheduling detail.
 */
#include <stdint.h>

static void cache_range(uint32_t address, int32_t length, uint32_t command)
{
    volatile uint32_t *const command_register =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f004);
    uint32_t line = (address & ~UINT32_C(15)) | command;
    while (length > 0) {
        *command_register = line;
        line += 16u;
        length -= 16;
    }
}

void gx8002_uart_stage2_cache_range_31d8(uint32_t address, int32_t length)
{
    cache_range(address, length, 2u);
}

void gx8002_uart_stage2_cache_range_3274(uint32_t address, int32_t length)
{
    cache_range(address, length, 8u);
}

void gx8002_uart_stage2_cache_range_3310(uint32_t address, int32_t length)
{
    cache_range(address, length, 10u);
}
