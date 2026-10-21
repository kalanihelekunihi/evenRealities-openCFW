/* SPDX-License-Identifier: MIT
 * Main 0x4c0f78 simple transfer-control selector branches.
 * The full dispatcher remains gated on the other selectors.
 */
#include <stdint.h>

static volatile uint32_t *reg(uint32_t module, uint32_t offset)
{
    return (volatile uint32_t *)(uintptr_t)
        (UINT32_C(0x40060000) + module * 0x1000u + offset);
}

uint32_t g2_main_mspi_transfer_control_candidate(uint32_t controller,
                                                 uint32_t selector,
                                                 const void *configuration)
{
    if (controller == 0u ||
        (*(const volatile uint32_t *)(uintptr_t)controller &
         UINT32_C(0x01ffffff)) != UINT32_C(0x01bebebe))
        return 2u;
    const uint32_t operation = selector & 0xffu;
    if (operation > 40u) return 6u;
    if (*(const volatile uint8_t *)(uintptr_t)(controller + 8u) == 0u)
        return 7u;
    if ((operation < 21u || operation > 23u) &&
        (operation < 35u || operation > 39u))
        return 6u;

    const uint32_t module =
        *(const volatile uint32_t *)(uintptr_t)(controller + 4u);
    volatile uint32_t *const flags = reg(module, 0x90u);
    switch (operation) {
    case 21:
        *flags |= 1u;
        return 0u;
    case 22:
        *reg(module, 0u) |= 0x100u;
        *flags |= 0x10u;
        *(volatile uint8_t *)(uintptr_t)(controller + 0xdu) = 1u;
        return 0u;
    case 23:
        *reg(module, 0u) &= ~UINT32_C(0x100);
        *flags &= ~UINT32_C(0x10);
        *(volatile uint8_t *)(uintptr_t)(controller + 0xdu) = 0u;
        return 0u;
    case 35: {
        if (configuration == 0) return 6u;
        const uint8_t *const cfg = (const uint8_t *)configuration;
        if (cfg[0] >= 4u || cfg[1] >= 2u) return 6u;
        volatile uint32_t *const format = reg(module, 0x84u);
        *format = (*format & UINT32_C(0xffffff7f)) |
                  ((uint32_t)(cfg[1] & 1u) << 7);
        *format = (*format & UINT32_C(0xffffff9f)) |
                  ((uint32_t)(cfg[0] & 3u) << 5);
        return 0u;
    }
    case 36: {
        if (configuration == 0) return 6u;
        const uint8_t *const cfg = (const uint8_t *)configuration;
        volatile uint32_t *const format = reg(module, 0x84u);
        *format = (*format & UINT32_C(0x03ffffff)) |
                  ((uint32_t)cfg[9] << 26);
        *flags = (*flags & UINT32_C(0xfffff0ff)) | 0x500u;
        *flags = (*flags & UINT32_C(0xffffdfff)) |
                 ((uint32_t)(cfg[12] & 1u) << 13);
        return 0u;
    }
    case 37:
        *flags &= ~UINT32_C(0x40);
        return 0u;
    case 38:
        *flags |= 0x40u;
        return 0u;
    case 39: {
        if (configuration == 0) return 6u;
        const uint8_t *const cfg = (const uint8_t *)configuration;
        volatile uint32_t *const word = reg(module, 0xa4u);
        if (cfg[4] == 0u) {
            *word &= ~UINT32_C(1);
            return 0u;
        }
        *word |= 1u;
        *word = (*word & UINT32_C(0xfffff9ff)) |
                ((uint32_t)(cfg[0] & 3u) << 9);
        *word &= UINT32_C(0xfffffff9);
        *word = (*word & UINT32_C(0xfffffff7)) |
                ((uint32_t)(cfg[1] & 1u) << 3);
        *word = (*word & UINT32_C(0xffffffef)) |
                ((uint32_t)(cfg[2] & 1u) << 4);
        *word = (*word & UINT32_C(0xffffffdf)) |
                ((uint32_t)(cfg[3] & 1u) << 5);
        *word &= UINT32_C(0xfffffe3f);
        return 0u;
    }
    default:
        return 6u;
    }
}
