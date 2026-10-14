/* SPDX-License-Identifier: MIT
 * Main 0x4c0f78 selectors 0..13: direct MSPI control-register operations.
 * The complete selector dispatcher remains unresolved until every branch is
 * source-owned.
 */
#include <stdint.h>

static volatile uint32_t *reg(uint32_t module, uint32_t offset)
{
    return (volatile uint32_t *)(uintptr_t)
        (UINT32_C(0x40060000) + module * 0x1000u + offset);
}

uint32_t g2_main_mspi_transfer_basic_candidate(uint32_t controller,
                                                 uint32_t selector,
                                                 const void *configuration)
{
    if (controller == 0u ||
        (*(const volatile uint32_t *)(uintptr_t)controller &
         UINT32_C(0x01ffffff)) != UINT32_C(0x01bebebe))
        return 2u;
    const uint8_t operation = (uint8_t)selector;
    if (operation > 40u)
        return 6u;
    if (*(const volatile uint8_t *)(uintptr_t)(controller + 8u) == 0u)
        return 7u;
    if (operation >= 14u)
        return 6u;
    const uint32_t module =
        *(const volatile uint32_t *)(uintptr_t)(controller + 4u);
    const uint32_t value = configuration ?
        *(const uint32_t *)configuration : 0u;
    volatile uint32_t *word;
    switch (operation) {
    case 0:
        if (!configuration) return 6u;
        word = reg(module, 0x30u);
        *word = (*word & ~1u) | ((uint8_t)value & 1u);
        return 0u;
    case 1:
        if (!configuration || (value & UINT32_C(0x00e0e0e0)))
            return 6u;
        *reg(module, 0x2b4u) = value;
        return 0u;
    case 2:
        if (!configuration || value > 7u) return 6u;
        word = reg(module, 0x30u);
        *word = (*word & UINT32_C(0xffffff0f)) |
                (((uint8_t)value & 0xfu) << 4);
        return 0u;
    case 3:
        if (!configuration || (value > 3u && value != 7u)) return 6u;
        word = reg(module, 0x30u);
        *word = (*word & UINT32_C(0xffffff0f)) |
                (((value + 8u) & 0xfu) << 4);
        return 0u;
    case 4:
        *reg(module, 0x90u) &= ~UINT32_C(0x1000);
        return 0u;
    case 5:
        *reg(module, 0x90u) |= UINT32_C(0x1000);
        return 0u;
    case 6:
        *reg(module, 0x9cu) &= ~UINT32_C(0x80000000);
        return 0u;
    case 7:
        *reg(module, 0x9cu) |= UINT32_C(0x80000000);
        return 0u;
    case 8:
        if (!configuration) return 6u;
        word = reg(module, 0x90u);
        *word = (*word & UINT32_C(0xfffffff3)) |
                (((uint8_t)value & 3u) << 2);
        return 0u;
    case 9:
        if (!configuration) return 6u;
        word = reg(module, 0x8cu);
        *word = (*word & UINT32_C(0xfff9ffff)) |
                (((uint8_t)value & 3u) << 17);
        return 0u;
    case 10:
        *reg(module, 0x8cu) &= ~UINT32_C(0x80000000);
        return 0u;
    case 11:
        *reg(module, 0x8cu) |= UINT32_C(0x80000000);
        return 0u;
    case 12:
        *reg(module, 0x88u) &= ~1u;
        return 0u;
    case 13:
        *reg(module, 0x88u) |= 1u;
        return 0u;
    default:
        return 6u;
    }
}
