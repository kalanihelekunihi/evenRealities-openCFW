/* Apollo Main Conversate animated prep-notes indicator, 0x58c7a0..0x58c835. */
#include <stdint.h>

/* Native RAM 0x20000bf4: six frame pointers. Source owner remains open. */
extern const void *audio_conversate_anim_frames_20000bf4[];
extern void *audio_terminal_voice_anim_create_597e90(void *);
extern void audio_lv_label_style_call_597ea6(void *, const void *, uint32_t);
extern void audio_lv_label_style_call_597f10(void *, uint32_t);
extern void audio_lv_label_style_call_597f52(void *, uint32_t);
extern uint32_t audio_conversate_route_get_release_pair_597f82(uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44127e(void *, uint32_t, uint32_t);
extern void audio_uart_page_44129e(void *, uint32_t, uint32_t);
extern void audio_lv_label_style_call_597ee0(void *);

uint32_t audio_conversate_pre_notes_anim_start_58c824(uint32_t object) {
    if (object == 0u) return 0u;
    audio_lv_label_style_call_597ee0((void *)(uintptr_t)object);
    return 1u;
}

uint32_t audio_conversate_pre_notes_anim_create_58c7a0(uint32_t parent,
                                                         uint32_t complete) {
    if (parent == 0u) return 0u;
    const uint32_t object = (uint32_t)(uintptr_t)audio_terminal_voice_anim_create_597e90(
        (void *)(uintptr_t)parent);
    if (object == 0u) return 0u;
    audio_lv_label_style_call_597ea6((void *)(uintptr_t)object,
                                     audio_conversate_anim_frames_20000bf4, 6u);
    audio_lv_label_style_call_597f10((void *)(uintptr_t)object, 600u);
    audio_lv_label_style_call_597f52((void *)(uintptr_t)object, 100u);
    const uint32_t pair = audio_conversate_route_get_release_pair_597f82(object);
    if (pair != 0u) {
        *(volatile uint32_t *)(uintptr_t)(pair + 0x40u) = 400u;
        if (complete != 0u)
            *(volatile uint32_t *)(uintptr_t)(pair + 0x10u) = complete;
    }
    const uint32_t color = audio_uart_page_44104c(0u);
    audio_uart_page_44127e((void *)(uintptr_t)object, color, 0u);
    audio_uart_page_44129e((void *)(uintptr_t)object, 0xffu, 0u);
    (void)audio_conversate_pre_notes_anim_start_58c824(object);
    return object;
}
