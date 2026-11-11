#include <stdint.h>

uint32_t audio_uart_ring_primary_list_cell
    __attribute__((section(".g2_ram_200746d4"), used));
uint32_t audio_uart_ring_primary_head_cell
    __attribute__((section(".g2_ram_200746dc"), used));
uint32_t audio_uart_ring_secondary_list_cell
    __attribute__((section(".g2_ram_200746d8"), used));
uint32_t audio_uart_ring_secondary_head_cell
    __attribute__((section(".g2_ram_200746e0"), used));
/* Stock 0x200746e0 is a single cell (literal pool 0x463bf0/0x469ba0/0x46b08c); alias so all users share it (Fix 31). */
extern uint32_t audio_system_alert_font_200746e0 __attribute__((alias("audio_uart_ring_secondary_head_cell")));
