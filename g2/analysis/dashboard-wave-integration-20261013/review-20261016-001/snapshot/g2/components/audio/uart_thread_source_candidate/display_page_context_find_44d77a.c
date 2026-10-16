/* Apollo active page input lookup 0x44d77a..0x44d7b5. */
#include <stdint.h>

extern void *audio_uart_lv_input_next_452edc(void *);

void *audio_uart_page_context_find_44d77a(void *page) {
    void *matched = 0;
    void *input = audio_uart_lv_input_next_452edc(0);
    while (input != 0) {
        if (*(const uint8_t *)input == 1u)
            return input;
        if (*(void *const *)(const void *)((const uint8_t *)input + 0xb8u) == page)
            matched = input;
        input = audio_uart_lv_input_next_452edc(input);
    }
    return matched;
}
