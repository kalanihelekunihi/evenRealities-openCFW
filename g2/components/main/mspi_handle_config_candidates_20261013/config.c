/* SPDX-License-Identifier: MIT
 * Main 0x4c08a8 MSPI handle configuration leaf. The caller can pass the
 * source-owned state row as the handle, so reads follow native write order.
 */
#include <stdint.h>

#define MSPI_REG_BASE UINT32_C(0x40060000)
#define MAIN_MSPI_STATE_BASE UINT32_C(0x200523d8)
#define MAIN_MSPI_STATE_STRIDE UINT32_C(0x8d0)

uint32_t g2_main_mspi_handle_config_4c08a8(uint32_t handle_address,
                                            uint32_t config_address)
{
    volatile uint32_t *const handle =
        (volatile uint32_t *)(uintptr_t)handle_address;
    const uint32_t module = handle[1];
    if ((handle[0] & UINT32_C(0x01ffffff)) != UINT32_C(0x01bebebe))
        return 2u;
    if (handle[0] & UINT32_C(0x02000000))
        return 7u;

    const uintptr_t registers = MSPI_REG_BASE + module * 0x1000u;
    volatile uint32_t *const option =
        (volatile uint32_t *)(registers + 0x90u);
    *option &= ~UINT32_C(1);
    *(volatile uint32_t *)(registers + 0x9cu) = 0u;
    *(volatile uint32_t *)(registers + 0x80u) = 0u;

    const volatile uint32_t *const config =
        (const volatile uint32_t *)(uintptr_t)config_address;
    const uintptr_t state_address = MAIN_MSPI_STATE_BASE +
                                    module * MAIN_MSPI_STATE_STRIDE;
    volatile uint32_t *const state = (volatile uint32_t *)state_address;
    state[6] = config[1];
    state[5] = config[0];

    if (handle[6] != 0u) {
        const uint32_t end = handle[6] + handle[5] * 4u;
        *(volatile uint8_t *)(handle_address + 0x8c8u) =
            (uint8_t)(end < UINT32_C(0x20080000));
        uint32_t value = ((handle[5] - 8u) * 4u) / 0x48u;
        if (value > 0x100u)
            value = 0x100u;
        *(volatile uint32_t *)(state_address + 0x858u) = value;
    }

    *(volatile uint8_t *)(state_address + 9u) =
        *(const volatile uint8_t *)(config_address + 8u);
    *(volatile uint8_t *)(state_address + 8u) = 1u;
    *(volatile uint8_t *)(state_address + 10u) = 0x1au;
    return 0u;
}
