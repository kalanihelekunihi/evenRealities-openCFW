/* Stock list-animation new-object preparation at 0x5894d6..0x58956d. */
#include <stdint.h>

extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern uint32_t audio_uart_lv_child_count_44ddea(void *);
extern int32_t audio_uart_lv_child_index_44de92(void *);
extern int32_t audio_uart_lv_obj_y_44e498(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern void *audio_uart_lv_child_get_44dce2(void *, uint32_t);
extern void audio_terminal_ui_scroll_to_view_44ea2e(void *, uint32_t);

void audio_terminal_list_anim_new_prepare_5894d6(void *object) {
    void *parent = audio_uart_lv_obj_parent_44dca2(object);
    uint32_t count = audio_uart_lv_child_count_44ddea(parent);
    int32_t index = audio_uart_lv_child_index_44de92(object);
    int32_t parent_y = audio_uart_lv_obj_y_44e498(parent);
    int32_t height = audio_uart_lv_obj_height_43fdda(object);
    int32_t parent_height = audio_uart_lv_obj_height_43fdda(parent);
    int32_t object_rows = parent_height / height;
    int32_t remaining = index - parent_y / height;
    if (remaining < 2) {
        if (index != 0) {
            audio_terminal_ui_scroll_to_view_44ea2e(
                audio_uart_lv_child_get_44dce2(parent, (uint32_t)(index - 1)), 1u);
        } else {
            audio_terminal_ui_scroll_to_view_44ea2e(object, 1u);
        }
    } else if ((uint32_t)remaining >= (uint32_t)(object_rows - 2)) {
        if ((uint32_t)index < count - 1u) {
            audio_terminal_ui_scroll_to_view_44ea2e(
                audio_uart_lv_child_get_44dce2(parent, (uint32_t)(index + 1)), 1u);
        } else {
            audio_terminal_ui_scroll_to_view_44ea2e(object, 1u);
        }
    } else {
        audio_terminal_ui_scroll_to_view_44ea2e(object, 1u);
    }
}
