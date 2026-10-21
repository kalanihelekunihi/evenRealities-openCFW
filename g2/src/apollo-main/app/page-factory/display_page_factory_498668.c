/* Apollo page factory 0x498668..0x49867f. The descriptor address is a
 * stock ROM binding; final source-owned layout must replace this literal. */
#include <stdint.h>

extern void *audio_uart_page_create_44cf98(const void *, void *);
extern void audio_uart_page_initialize_44d0f0(void *);

void *audio_uart_page_498668(void *parent) {
    void *const page = audio_uart_page_create_44cf98(
        (const void *)(uintptr_t)0x00756108u, parent);
    audio_uart_page_initialize_44d0f0(page);
    return page;
}
