/* Apollo Main board callback, 0x444684..0x44468f. The stock pointer word
 * at 0x4448bc is 0x444685. Its indirect target is RAM 0x200742f0,
 * read through the stock 0x4448b8 literal. Ambiq stdio identifies the same
 * cell as g_pfnCharPrint (see main_formatter_offline/format.c). */
#include <stdint.h>

volatile uint32_t audio_uart_stdio_print_char_cell_200742f0
    __attribute__((section(".g2_ram_200742f0"), aligned(4)));

void audio_uart_display_board_callback_444684(uint32_t ignored,
                                               uint32_t value) {
    (void)ignored;
    void (*target)(char *) =
        (void (*)(char *))(uintptr_t)audio_uart_stdio_print_char_cell_200742f0;
    target((char *)(uintptr_t)value);
}

const void *audio_uart_display_board_data =
    (const void *)(uintptr_t)&audio_uart_display_board_callback_444684;
