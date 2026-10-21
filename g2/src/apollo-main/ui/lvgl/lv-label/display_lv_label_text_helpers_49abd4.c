/* Native LV label helpers 0x49abd4 and 0x49abe0. */
#include <stdint.h>

extern uint32_t audio_uart_lv_string_length_454768(const char *);
extern char *strcpy(char *, const char *);

uint32_t audio_uart_page_text_length_49abd4(const char *text) {
    return audio_uart_lv_string_length_454768(text) + 1u;
}

void audio_uart_page_text_content_init_49abe0(uint8_t *page,
                                                const char *text) {
    char *const destination = *(char **)(void *)(page + 0x2cu);
    (void)strcpy(destination, text);
}
