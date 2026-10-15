#include <stdint.h>

/* Native sync_timer_start literals identify three separate pointer cells. */
void *audio_uart_sync_timer_sem
    __attribute__((section(".g2_ram_200749d4"), used));
void *audio_uart_sync_timer_handle
    __attribute__((section(".g2_ram_200749d8"), used));
void *audio_uart_sync_timer_event
    __attribute__((section(".g2_ram_20074b10"), used));
