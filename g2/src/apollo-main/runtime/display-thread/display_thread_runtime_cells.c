#include <stdint.h>

uint8_t audio_uart_display_message[12]
    __attribute__((section(".g2_ram_20073fcc"), used));
void *audio_uart_display_mutex
    __attribute__((section(".g2_ram_200744e8"), used));
uint8_t audio_uart_display_framebuffer[0x2800]
    __attribute__((section(".g2_ram_2034dc30"), used));
void *audio_uart_display_instance
    __attribute__((section(".g2_ram_200746b8"), used));
/* Stock 0x200744e8 is a single cell (pool 0x4443c8/0x4448a0); alias so all users share it. */
extern void *audio_uart_input_mutex __attribute__((alias("audio_uart_display_mutex")));
/* Stock 0x200744e8 is a single cell (literal pool 0x4443c8/0x4448a0); alias so all users share it (Fix 31). */
extern void * g2_display_sender_mutex __attribute__((alias("audio_uart_display_mutex")));
