/* SPDX-License-Identifier: MIT. Main 0x4c2098 PIO control path, adapted from bootloader 0x4262e0.
 * FIFO movement and timed status polling are explicit downstream providers;
 * no peripheral or elapsed-time claim follows from this source alone.
 */
#include <stdint.h>
extern uint32_t g2_main_mspi_fifo_read_4bfbbc(uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t g2_main_mspi_fifo_write_4bfb72(uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t g2_main_mspi_status_poll_480826(uint32_t, uintptr_t, uint32_t, uint32_t, uint32_t);
uint32_t g2_norflash_transfer_4c2098(uint32_t address,
                                          const uint8_t *pio,
                                          uint32_t timeout) {
    const uint32_t *handle = (const uint32_t *)(uintptr_t)address;
    if (!handle || (handle[0] & 0x01ffffffu) != 0x01bebebeu) return 2;
    const uint8_t *state = (const uint8_t *)handle;
    if ((state[10] == 10u || state[10] == 11u) && (pio[8] & 3u)) return 7;
    if (pio[18] != 0u || handle[8] != 0u || handle[0x210] != 0u ||
        state[0x82c] == 2u) return 7;
    const uint32_t *words = (const uint32_t *)pio;
    uintptr_t base = 0x40060000u + (handle[1] << 12);
    volatile uint32_t *registers = (volatile uint32_t *)base;
    uint32_t control = (words[0] << 16) | ((uint32_t)pio[4] << 9) |
                       (((uint32_t)pio[6] << 7) & 0x80u);
    if (pio[12]) {
        control |= 0x40u;
        registers[3] = *(const uint16_t *)(const void *)(pio + 14);
    }
    if (pio[7]) { control |= 0x20u; registers[2] = words[2]; }
    if (pio[16]) control |= 0x400u;
    control |= (uint32_t)state[13] << 8;
    control |= (uint32_t)pio[17] << 12;
    if (pio[5]) control |= 0x800u;
    uint32_t enabled = registers[0x200 / 4];
    registers[0x200 / 4] = 0;
    registers[0x208 / 4] = UINT32_MAX;
    registers[0] = control | 1u;
    uint32_t status = 0;
    if (pio[6] == 0u)
        status = g2_main_mspi_fifo_read_4bfbbc(handle[1], words[5], words[0], handle[4]);
    else if (pio[6] == 1u)
        status = g2_main_mspi_fifo_write_4bfb72(handle[1], words[5], words[0], handle[4]);
    /* Other direction bytes still trigger stock status polling; no added guard. */
    if (status == 0u) status = g2_main_mspi_status_poll_480826(timeout, base, 2u, 2u, 1u);
    registers[0x208 / 4] = UINT32_MAX;
    registers[0x200 / 4] = enabled;
    return status;
}
