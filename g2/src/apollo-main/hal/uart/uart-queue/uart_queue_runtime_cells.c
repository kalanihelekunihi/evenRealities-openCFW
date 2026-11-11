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
/* Stock 0x200749c4 is a single cell (pool 0x45dd64/0x45ebdc); alias so all users share it. */
extern void *g2_uart_sync_module __attribute__((alias("g2_uart_tinyframe")));
/* Stock 0x200749cc is a single cell (pool 0x45d068/0x45ebc8/0x4651c0); alias so all users share it. */
extern void *audio_uart_sync_schedule_queue __attribute__((alias("g2_uart_send_queue")));
/* Stock 0x200749cc is a single cell (literal pool 0x45d068/0x45ebc8/0x4651c0); alias so all users share it (Fix 31). */
extern void * audio_settings_peer_send_queue __attribute__((alias("g2_uart_send_queue")));
