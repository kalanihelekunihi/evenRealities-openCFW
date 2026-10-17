/* Native prep-note line measure 0x5b3f94..0x5b3fff. */
#include <stdint.h>

extern uint32_t audio_uart_ring_primary_head_cell;
extern uint32_t audio_uart_text_line_length_4897fc(const char *, uint32_t,
                                                    const void *, int32_t,
                                                    int32_t, uint32_t, uint32_t);
extern uint32_t audio_conversate_prep_note_utf8_prefix_5b3ef8(
    const void *, uint32_t);

uint32_t audio_conversate_prep_note_measure_line_5b3f94(const void *text,
                                                         uint32_t length,
                                                         uint32_t width) {
    uint16_t available = (uint16_t)length;
    if (available == 0u)
        return 0u;
    uint32_t result = audio_uart_text_line_length_4897fc(
        text, available, (const void *)(uintptr_t)audio_uart_ring_primary_head_cell,
        0, (int32_t)width, 0u, 0u);
    if (result != 0u)
        return (uint16_t)(result < available ? result : available);
    uint16_t fallback = available < 4u ? available : 4u;
    result = (uint16_t)audio_conversate_prep_note_utf8_prefix_5b3ef8(text, fallback);
    if (result == 0u)
        return 1u;
    return result;
}
