/* Apollo Main LVGL heap pool cell: stock wrappers 0x48431e/32a/338 all
 * load 0x20000338. The existing heap initializer owns the 0x1c-byte cell.
 * An absolute assembler symbol represents its fixed SRAM address without
 * allocating a second C object at an unrelated address. */
#include <stdint.h>

enum { AUDIO_UART_LV_HEAP_POOL_RAM = 0x20000338u };
_Static_assert(AUDIO_UART_LV_HEAP_POOL_RAM % 4u == 0u,
               "LVGL heap pool cell must be word aligned");

/* sim15: the pool is the start of g2_stock_ram_20000338 (system/stock-ram/
 * stock_ram_cells.c), which display_font_alloc.c initializes via
 * audio_uart_lv_pool_initialize_48413c. Binding to the raw address read an
 * unrelated object in our layout (dmFcnIfTbl region -> sem 0x67f050 fault). */
/* Consumers now declare audio_uart_lv_heap_pool with __asm__("g2_stock_ram_20000338"). */
