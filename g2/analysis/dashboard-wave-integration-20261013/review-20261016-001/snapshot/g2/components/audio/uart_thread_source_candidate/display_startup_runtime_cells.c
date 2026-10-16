#include <stdint.h>

void *g2_display_queue
    __attribute__((section(".g2_ram_200744e4"), used));
uint8_t g2_display_queue_control[0x50]
    __attribute__((section(".g2_ram_200729e8"), used));
uint8_t g2_display_queue_storage[0x480]
    __attribute__((section(".g2_ram_203780c0"), used));
uint8_t g2_display_ring_storage[0xa000]
    __attribute__((section(".g2_ram_200e99b4"), used));
void *audio_uart_display_surface
    __attribute__((section(".g2_ram_200746b4"), used));
void *audio_uart_display_lock
    __attribute__((section(".g2_ram_200746bc"), used));
