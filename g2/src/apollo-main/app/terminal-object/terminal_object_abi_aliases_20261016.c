/* Terminal legacy names for already C-bound LVGL providers at stock addresses. */
#include <stdint.h>
extern void audio_uart_page_43ded4(void *, uint32_t);
extern void audio_uart_display_audio_reset_441488(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_lv_style_unlink_450500(void *, void *);
extern void audio_uart_page_delete_event_filter_44d7b8(void *);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
void audio_lv_object_call_43ded4(uint32_t object, uint32_t flags) {
    audio_uart_page_43ded4((void *)(uintptr_t)object, flags);
}
void audio_lv_object_call_441488(uint32_t object, uint32_t opacity,
                                  uint32_t selector) {
    audio_uart_display_audio_reset_441488(object, opacity, selector);
}
void audio_lv_object_call_450500(uint32_t object, uint32_t style) {
    (void)audio_uart_lv_style_unlink_450500((void *)(uintptr_t)object,
                                            (void *)(uintptr_t)style);
}
void audio_lv_object_release_44d7b8(uint32_t object) {
    audio_uart_page_delete_event_filter_44d7b8((void *)(uintptr_t)object);
}
void audio_lv_object_size_call_43f4c0(uint32_t object, uint32_t width,
                                       uint32_t height) {
    audio_uart_page_43f4c0(object, width, height);
}
