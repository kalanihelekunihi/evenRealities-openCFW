#include <stdint.h>

/* audio_uart_device_role_cell is stock 0x20075024 (role_get 0x45a6c8 strb via
   pool 0x45b0f4); defined as an alias of g2_audio_service_mode in
   service_mode_state.c so the reader and writer share one cell. */
volatile uint32_t audio_uart_lcd_status_cell
    __attribute__((section(".g2_ram_20074edc"), used));
volatile uint32_t audio_uart_display_audio_lock_cell
    __attribute__((section(".g2_ram_200749c8"), used));
volatile uint32_t audio_uart_display_audio_flag_cell
    __attribute__((section(".g2_ram_200749e4"), used));
