#include <stdint.h>

void *audio_uart_font_flash_device
    __attribute__((section(".g2_ram_20074544"), used));
void * volatile audio_uart_font_flash_mutex
    __attribute__((section(".g2_ram_20074548"), used));
/* Stock 0x20074544 is a single cell (literal pool 0x470014/0x4708a4/0x4710ac); alias so all users share it (Fix 31). */
extern uint32_t g2_norflash_controller_handle_20074544 __attribute__((alias("audio_uart_font_flash_device")));
