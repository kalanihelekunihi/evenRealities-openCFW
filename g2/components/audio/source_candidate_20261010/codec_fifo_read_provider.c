#include <stdint.h>

/* Apollo MAIN 0x58e2d8: one GX8002 codec RX FIFO instance. */
uint32_t codec_fifo_read(const void *handle, uint8_t *buffer,
                         uint32_t length, uint32_t *received) {
    uint32_t instance = *(const uint32_t *)((const uint8_t *)handle + 0x28u);
    volatile uint32_t *fifo = (volatile uint32_t *)(uintptr_t)
        (0x40039000u + (instance << 12));
    uint32_t count = 0;
    uint32_t status = 0;
    while (count < length) {
        if ((fifo[6] >> 4) & 1u)
            break;
        uint32_t sample = fifo[0];
        if (sample & 0xF00u) {
            status = 0x08000000u;
            break;
        }
        if (buffer)
            buffer[count++] = (uint8_t)sample;
    }
    if (received)
        *received = count;
    return status;
}
