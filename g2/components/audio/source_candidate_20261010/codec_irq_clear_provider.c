/* Apollo MAIN 0x58E7E4: UART codec interrupt clear. */
#include <stdint.h>

uint32_t codec_irq_clear(const uint8_t *handle, uint32_t mask) {
    /* Original reads the instance word before testing the handle pointer. */
    uint32_t instance = *(volatile const uint32_t *)(handle + 0x28);
    if (!handle || (*(volatile const uint32_t *)handle & 0x01ffffffu) != 0x01ea9e06u)
        return 2;
    volatile uint32_t * const registers =
        (volatile uint32_t *)(uintptr_t)(0x40039000u + (instance << 12));
    registers[0x44u / 4u] = mask;
    (void)registers[0x40u / 4u];
    return 0;
}
