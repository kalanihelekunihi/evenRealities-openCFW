/* SPDX-License-Identifier: MIT
 * Main 0x4c0812 MSPI handle initialization. The caller at 0x46fb0c passes
 * the fixed NOR controller word at 0x20074544 as the output slot.
 */
#include <stdint.h>

#define MAIN_MSPI_STATE_BASE UINT32_C(0x200523d8)
#define MAIN_MSPI_STATE_STRIDE UINT32_C(0x8d0)

uint32_t g2_main_mspi_handle_init_4c0812(uint32_t module,
                                          uint32_t *handle_slot)
{
    if (module >= 4u)
        return 5u;
    if (handle_slot == 0)
        return 6u;

    const uintptr_t state_address = MAIN_MSPI_STATE_BASE +
                                    module * MAIN_MSPI_STATE_STRIDE;
    volatile uint32_t *const state = (volatile uint32_t *)state_address;
    if (state[0] & UINT32_C(0x01000000))
        return 7u;

    state[0] = (state[0] & UINT32_C(0xff000000)) |
               UINT32_C(0x01000000) | UINT32_C(0x00bebebe);
    state[1] = module;
    *(volatile uint8_t *)(state_address + 0xcu) = 0u;
    state[6] = 0u;
    *(volatile uint8_t *)(state_address + 0x8c9u) = 7u;
    *(volatile uint32_t *)(state_address + 0x8ccu) = 8u;
    *handle_slot = (uint32_t)state_address;
    return 0u;
}
