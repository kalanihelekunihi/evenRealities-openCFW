#include <stdint.h>

/* Native sync_timer_start literals identify three separate pointer cells. */
void *audio_uart_sync_timer_sem
    __attribute__((section(".g2_ram_200749d4"), used));
void *audio_uart_sync_timer_handle
    __attribute__((section(".g2_ram_200749d8"), used));
void *audio_uart_sync_timer_event
    __attribute__((section(".g2_ram_20074b10"), used));
/* Stock 0x200749d4 is a single cell (pool 0x45dd38); alias so all users share it. */
extern void *g2_uart_sync_semaphore __attribute__((alias("audio_uart_sync_timer_sem")));
/* Stock 0x20074b10 is a single cell (pool 0x45d0c8/0x45df14/0x465470); alias so all users share it. */
extern void *audio_uart_input_event_flags __attribute__((alias("audio_uart_sync_timer_event")));
/* Stock 0x20074b10 is a single cell (pool 0x45d0c8/0x45df14/0x465470); alias so all users share it. */
extern void *g2_uart_thread_event __attribute__((alias("audio_uart_sync_timer_event")));
/* Stock 0x20074b10 is a single cell (literal pool 0x45d0c8/0x45df14/0x465470); alias so all users share it (Fix 31). */
extern void * audio_settings_peer_event __attribute__((alias("audio_uart_sync_timer_event")));
