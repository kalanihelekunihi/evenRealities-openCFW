/* SPDX-License-Identifier: MIT
 * Main 0x4c0e1e/0x4c0ea8 MSPI enable/disable, adapted from authenticated
 * bootloader HAL leaves. Command-queue operations remain named lowers.
 */
#include <stdint.h>

extern void g2_main_mspi_cq_init_4bfc5a(uint32_t, uint32_t, uint32_t);
extern uint32_t g2_main_mspi_cq_disable_4bfd62(uint32_t);
extern void g2_main_mspi_cq_term_4bfc86(uint32_t);
extern void audio_delay_us_selected(uint32_t);

static uint32_t valid(const uint32_t *handle)
{
    return handle && (handle[0] & 0x01ffffffu) == 0x01bebebeu;
}

static volatile uint32_t *reg(const uint32_t *handle, uint32_t offset)
{
    return (volatile uint32_t *)(uintptr_t)
        (0x40060000u + (handle[1] << 12) + offset);
}

uint32_t g2_norflash_enable_mspi_4c0e1e(uint32_t address)
{
    uint32_t *handle = (uint32_t *)(uintptr_t)address;
    if (!valid(handle)) return 2u;
    if (((uint8_t *)handle)[8] == 0u) return 7u;
    if (handle[6] != 0u) {
        handle[7] = handle[8] = 0u;
        g2_main_mspi_cq_init_4bfc5a(handle[1], handle[5], handle[6]);
        *reg(handle, 0x2b4u) = 0x00400080u;
        handle[0x215] = 0u;
        ((uint8_t *)handle)[0x83c] = 0u;
        handle[0x211] = handle[0x20e] = handle[0x210] = 0u;
        ((uint8_t *)handle)[0x82c] = 0u;
        handle[0x20c] = 0u;
        ((uint8_t *)handle)[0x82d] = 1u;
        handle[0x217] = 0u;
    }
    handle[0] |= 0x02000000u;
    return 0u;
}

uint32_t g2_norflash_disable_mspi_4c0ea8(uint32_t address)
{
    uint32_t *handle = (uint32_t *)(uintptr_t)address;
    if (!valid(handle)) return 2u;
    if (!(handle[0] & 0x02000000u)) return 0u;
    if (handle[0x210] != 0u || handle[8] != 0u) return 3u;
    if (handle[6] != 0u) {
        uint32_t status = g2_main_mspi_cq_disable_4bfd62(address);
        if (status != 0u) return status;
        g2_main_mspi_cq_term_4bfc86(address);
    }
    handle[0] &= ~0x02000000u;
    if (*reg(handle, 0x90u) & 1u)
        audio_delay_us_selected(handle[0x233]);
    return 0u;
}
