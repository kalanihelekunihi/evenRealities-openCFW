#include <stdint.h>

/* Native 0x20073b48 precedes the independently identified ring at 0x20073b60. */
uint8_t audio_uart_display_control[24]
    __attribute__((section(".g2_ram_20073b48"), used));

const char audio_uart_display_lock_function[] = "display_buffer_lock_init";
