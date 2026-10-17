/* Apollo Main LVGL heap pool cell: stock wrappers 0x48431e/32a/338 all
 * load 0x20000338. The existing heap initializer owns the 0x1c-byte cell.
 * An absolute assembler symbol represents its fixed SRAM address without
 * allocating a second C object at an unrelated address. */
#include <stdint.h>

enum { AUDIO_UART_LV_HEAP_POOL_RAM = 0x20000338u };
_Static_assert(AUDIO_UART_LV_HEAP_POOL_RAM % 4u == 0u,
               "LVGL heap pool cell must be word aligned");

__asm__(".global audio_uart_lv_heap_pool\n"
        ".set audio_uart_lv_heap_pool, 0x20000338\n");
