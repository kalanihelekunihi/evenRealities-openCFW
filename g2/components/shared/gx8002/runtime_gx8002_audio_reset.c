/* SPDX-License-Identifier: MIT */
/* Reconstructed ordered MMIO reset from the stock GX8002 _ain_reset routine.
 * Its 320-byte section is independently identified by authenticated SDK
 * object evidence. No object bytes or binary-derived arrays are emitted.
 * Candidate only: requires decoded MMIO trace and wait-loop qualification. */
#include <stdint.h>
#define AUDIO_REG(offset) (*(volatile uint32_t *)(uintptr_t)(0xa0a00000u + (offset)))
#define SET_BIT(offset, bit) (AUDIO_REG(offset) |= UINT32_C(1) << (bit))
#define CLEAR_BIT(offset, bit) (AUDIO_REG(offset) &= ~(UINT32_C(1) << (bit)))
int open_cfw_gx8002_audio_reset(void)
{
    AUDIO_REG(0x100) = 0;
    AUDIO_REG(0x104) = ~UINT32_C(0x700);
    CLEAR_BIT(0x000, 31);
    SET_BIT(0x000, 15);
    CLEAR_BIT(0x000, 14);
    SET_BIT(0x000, 7);
    CLEAR_BIT(0x000, 6);
    SET_BIT(0x004, 31);
    CLEAR_BIT(0x004, 30);
    SET_BIT(0x008, 31);
    CLEAR_BIT(0x008, 30);
    CLEAR_BIT(0x00c, 9);
    CLEAR_BIT(0x028, 9);
    CLEAR_BIT(0x02c, 9);
    CLEAR_BIT(0x048, 9);
    CLEAR_BIT(0x04c, 9);
    AUDIO_REG(0x104) = UINT32_C(0x200);
    while ((AUDIO_REG(0x104) & UINT32_C(0x100)) == 0) {
        /* Stock waits indefinitely for this hardware status bit. */
    }
    AUDIO_REG(0x104) = UINT32_C(0x100);
    AUDIO_REG(0x104) = UINT32_C(0x400);
    AUDIO_REG(0x104) = UINT32_C(0x071f003f);
    SET_BIT(0x108, 15);
    CLEAR_BIT(0x108, 14);
    SET_BIT(0x108, 7);
    CLEAR_BIT(0x108, 6);
    SET_BIT(0x108, 23);
    CLEAR_BIT(0x108, 22);
    SET_BIT(0x158, 31);
    CLEAR_BIT(0x158, 30);
    SET_BIT(0x180, 31);
    CLEAR_BIT(0x180, 30);
    CLEAR_BIT(0x180, 29);
    return 0;
}
