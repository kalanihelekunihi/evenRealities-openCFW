#include <stdint.h>

void *g2_uart_tinyframe
    __attribute__((section(".g2_ram_200749c4"), used));
void *g2_uart_send_queue
    __attribute__((section(".g2_ram_200749cc"), used));
uint8_t g2_uart_send_queue_control[0x50]
    __attribute__((section(".g2_ram_20072df8"), used));
uint8_t g2_uart_send_queue_storage[0x258]
    __attribute__((section(".g2_ram_2006e860"), used));
volatile uint8_t audio_uart_ring_worn
    __attribute__((section(".g2_ram_2007500c"), used));
