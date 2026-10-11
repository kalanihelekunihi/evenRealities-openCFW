/* SPDX-License-Identifier: MIT
 * UART stage-2 request dispatcher at 0x10004db8. The native 10-entry jump
 * table at 0x1000820c is represented by these typed cases.
 */
#include <stdint.h>

uint32_t gx8002_uart_stage2_analog_request_4db8(uint32_t kind,
                                                    const uint8_t *request)
{
    volatile uint32_t *const analog =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0000000);
    switch (kind) {
    case 0:
        for (unsigned i = 0; i < 8u; ++i) {
            const uint32_t value = (uint32_t)request[i * 2u] |
                                   ((uint32_t)request[i * 2u + 1u] << 8);
            analog[1u + i] = value;
        }
        return 0;
    case 1: case 2: case 3: case 4: case 8: {
        const uint32_t value = *(const volatile uint32_t *)(const void *)request;
        const unsigned offset = kind == 8u ? 0x38u :
                                kind == 4u ? 0x34u : 0x24u + (kind - 1u) * 4u;
        analog[offset / 4u] = value;
        return 0;
    }
    case 5: {
        volatile uint32_t *const pmu =
            (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010000);
        pmu[0x58 / 4] = request[0] & 1u;
        pmu[0x5c / 4] = *(const volatile uint32_t *)(const void *)(request + 4);
        return 0;
    }
    case 6:
        return UINT32_MAX;
    case 7:
        analog[0x4c / 4] = (uint32_t)request[4] | ((uint32_t)request[5] << 8);
        analog[0x48 / 4] = ((uint32_t)request[3] << 4) | request[2];
        analog[0x44 / 4] = request[1] != 0u;
        analog[0x40 / 4] = request[0] != 0u;
        return 0;
    case 9: {
        analog[0x3c / 4] =
            (*(const volatile uint32_t *)(const void *)request) & 1u;
        *(volatile uint32_t *)(uintptr_t)UINT32_C(0x2000996c) =
            (*(const volatile uint32_t *)(const void *)request) & 1u;
        return 0;
    }
    default:
        return UINT32_MAX;
    }
}
