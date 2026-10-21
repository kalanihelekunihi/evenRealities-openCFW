/* Apollo MAIN 0x58E80E: UART codec interrupt status selector. */
#include <stdint.h>

uint32_t codec_irq_status(const uint8_t *handle, uint32_t *out, uint32_t raw) {
    /* Preserve original handle+0x28 read before tag/null checks. */
    uint32_t instance = *(volatile const uint32_t *)(handle + 0x28);
    if (!handle || (*(volatile const uint32_t *)handle & 0x01ffffffu) != 0x01ea9e06u)
        return 2;
    volatile uint32_t * const registers =
        (volatile uint32_t *)(uintptr_t)(0x40039000u + (instance << 12));
    *out = ((uint8_t)raw ? registers[0x40u / 4u] : registers[0x3cu / 4u]);
    return 0;
}
