/* Apollo Main LVGL child deletion, native span 0x44df80..0x44e139.
 * The stock recursive BL at 0x44dfce receives the child in R0 from
 * 0x44dce2; Ghidra omitted this live argument. */
#include <stdint.h>

extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);
extern void audio_uart_lv_style_destroy_450228(void *);
extern void *audio_uart_lv_child_get_44dce2(void *, uint32_t);
extern void *audio_uart_lv_obj_group_43e1be(void *);
extern void *audio_uart_lv_input_next_452edc(void *);
extern void audio_uart_lv_input_unlink_44df60(void *, void *);
extern void *audio_uart_lv_input_active_452ffa(void);
extern uint32_t audio_uart_lv_cleanup_matching_484052(void *, void *);
extern void audio_uart_lv_obj_delete_cleanup_44d16e(void *);
extern void *audio_uart_lv_display_for_object(void *);
extern uint32_t audio_uart_lv_child_index_44de92(void *);
extern void *audio_uart_lv_realloc_44f76a(void *, uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);
extern void audio_uart_page_delete_event_filter_44d7b8(void *);


void audio_uart_lv_delete_event_callback_44df20(void *object) {
    if (object == 0) {
        audio_uart_lvgl_log(3u, "lv_obj_delete", 0x257u,
                            "lv_obj_delete_async_cb", "object is null");
        __builtin_trap();
    }
    audio_uart_page_delete_event_filter_44d7b8(object);
}


