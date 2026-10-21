#include <stdint.h>

/* Complete native 0x00592462..0x00592483. */
uint32_t g2_pdm_prepare_clock(void *handle, uint32_t value) {
    const uint32_t *const row = (const uint32_t *)handle;
    if (handle == 0 || (row[0] & 0x01ffffffu) != 0x01f956e2u)
        return 2u;
    uint32_t const instance = row[2];
    *(volatile uint32_t *)(uintptr_t)
        (0x40201000u + (instance << 12) + 0x1cu) = value;
    return 0u;
}
