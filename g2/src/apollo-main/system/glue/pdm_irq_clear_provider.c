/* Apollo MAIN 0x5925B4: PDM interrupt clear with handle tag check. */
#include <stdint.h>

uint32_t audio_pdm_interrupt_clear(const uint32_t *handle, uint32_t mask) {
    if (!handle || (handle[0] & 0x01ffffffu) != 0x01f956e2u) return 2;
    uint32_t instance = handle[2];
    volatile uint32_t * const registers =
        (volatile uint32_t *)(uintptr_t)(0x40201000u + (instance << 12));
    registers[0x108u / 4u] = mask;
    (void)registers[0x104u / 4u];
    return 0;
}
