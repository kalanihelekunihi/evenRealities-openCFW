/* Apollo Main animation cancel matching, native span 0x450a74..0x450b0b. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_state[];
extern void *audio_uart_lv_list_first(void *);
extern void *audio_uart_lv_list_next(void *, void *);
extern void audio_uart_lv_list_remove(void *, void *);
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_lv_transition_schedule_4509da(void);

static uint32_t word(const uint8_t *bytes, uint32_t offset) {
    return *(const uint32_t *)(const void *)(bytes + offset);
}

uint32_t audio_uart_lv_anim_cancel_matching_450a74(void *descriptor) {
    const uint8_t *const input = (const uint8_t *)descriptor;
    const uint32_t exec = word(input, 4u);
    if (exec == 0u && word(input, 8u) == 0u) return 0u;
    uint8_t *const list = audio_uart_display_lv_state + 0xacu;
    uint32_t removed = 0u;
    uint8_t *node = (uint8_t *)audio_uart_lv_list_first(list);
    while (node != 0) {
        const uint32_t match = node != input &&
            ((int32_t)word(node, 0x34u) >= 0 || (node[0x5cu] & 0x10u) != 0u) &&
            word(node, 0u) == word(input, 0u) &&
            word(node, 4u) != 0u && word(node, 4u) == exec;
        if (match) {
            audio_uart_lv_list_remove(list, node);
            const uint32_t completion = word(node, 0x14u);
            if (completion != 0u)
                ((void (*)(void *))(uintptr_t)completion)(node);
            audio_uart_lv_heap_free(node);
            audio_uart_lv_transition_schedule_4509da();
            removed = 1u;
            node = (uint8_t *)audio_uart_lv_list_first(list);
        } else {
            node = (uint8_t *)audio_uart_lv_list_next(list, node);
        }
    }
    return removed;
}
