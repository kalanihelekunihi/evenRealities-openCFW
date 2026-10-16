/* Observed LVGL runtime state prefix shared by three interior native cells. */
#include <stdint.h>

/* +0x64 static slot, +0xb8 tick state, +0x1d0 lock cell.
 * The 0x1d4 extent covers only observed accesses, not a full allocation map. */
uint8_t audio_uart_display_lv_state[0x1d4]
    __attribute__((section(".g2_ram_2006f548"), aligned(4)));
