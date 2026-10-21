#include <stdint.h>

uint8_t audio_uart_display_message[12]
    __attribute__((section(".g2_ram_20073fcc"), used));
void *audio_uart_display_mutex
    __attribute__((section(".g2_ram_200744e8"), used));
uint8_t audio_uart_display_framebuffer[0x2800]
    __attribute__((section(".g2_ram_2034dc30"), used));
void *audio_uart_display_instance
    __attribute__((section(".g2_ram_200746b8"), used));
