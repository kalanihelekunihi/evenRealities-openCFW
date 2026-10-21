#include <stdint.h>

volatile uint8_t audio_uart_device_role_cell
    __attribute__((section(".g2_ram_20075024"), used));
volatile uint32_t audio_uart_lcd_status_cell
    __attribute__((section(".g2_ram_20074edc"), used));
volatile uint32_t audio_uart_display_audio_lock_cell
    __attribute__((section(".g2_ram_200749c8"), used));
volatile uint32_t audio_uart_display_audio_flag_cell
    __attribute__((section(".g2_ram_200749e4"), used));
