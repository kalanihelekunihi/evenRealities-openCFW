/* Stock terminal processing label helper, 0x5ebfe0..0x5ebff7. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern const char *audio_uart_page_49942e(uint8_t *, const char *);

static const char processing[] = "[Processing]";

void audio_terminal_ui_processing_label_5ebfe0(void) {
    uint32_t label = *(const uint32_t *)(const void *)(audio_terminal_ui_state_base + 0x204u);
    if (label != 0u)
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)label, processing);
}
