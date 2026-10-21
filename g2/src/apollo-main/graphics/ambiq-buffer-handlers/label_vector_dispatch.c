/* Apollo Ambiq label vector glyph gate at native 0x53d6ea. */
#include <stdint.h>
extern uint32_t audio_uart_ambiq_outline_available_529ca4(uint32_t);
extern void audio_uart_ambiq_label_vector_draw_53d708(void *,void *);
void audio_uart_ambiq_label_vector_dispatch_53d6ea(void *unit,void *glyph) {
    uint32_t entry=*(const uint32_t *)(uintptr_t)
        *(const uint32_t *)((const uint8_t *)glyph+0x10u);
    if(audio_uart_ambiq_outline_available_529ca4(entry)!=0u)
        audio_uart_ambiq_label_vector_draw_53d708(unit,glyph);
}
