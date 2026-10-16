/* Apollo main 0x43f6d6: relative object alignment. Stock-derived control flow. */
#include <stdint.h>

extern void audio_uart_page_43f66c(uint32_t);
extern uint32_t audio_uart_lv_obj_parent_44dca2(uint32_t);
extern int32_t audio_uart_lv_style_pad_left_43efc6(uint32_t, uint32_t);
extern int32_t audio_uart_lv_style_pad_top_43f022(uint32_t, uint32_t);
extern uint32_t audio_uart_lv_style_base_dir_43efba(uint32_t, uint32_t);
extern int32_t audio_uart_lv_obj_width_43fd9e(uint32_t);
extern int32_t audio_uart_lv_obj_height_43fdda(uint32_t);
extern int32_t audio_uart_lv_obj_content_width_43fe16(uint32_t);
extern int32_t audio_uart_lv_obj_content_height_43fe70(uint32_t);
extern int32_t audio_uart_lv_scroll_right_44e67a(uint32_t);
extern int32_t audio_uart_lv_scroll_left_44e586(uint32_t);
extern int32_t audio_uart_lv_scroll_top_44e4aa(uint32_t);
extern void audio_uart_page_4411d4(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f09a(uint32_t, int32_t, int32_t);

static int32_t percent_offset(uint32_t encoded, uint32_t reference,
                              int32_t (*dimension)(uint32_t)) {
    uint32_t value = encoded & ~0x60000000u;
    if ((encoded & 0x60000000u) != 0x20000000u ||
        (int32_t)value >= 0x1fffffff) return (int32_t)encoded;
    int32_t extent = dimension(reference);
    if ((int32_t)value >= 0x10000000) value = 0x0fffffffu - value;
    return (int32_t)((int32_t)(value * (uint32_t)extent) / 100);
}

void audio_uart_page_43f6d6(uint32_t object, uint32_t reference,
                            uint32_t alignment, uint32_t x_offset,
                            uint32_t y_offset) {
    /* Stock reports an assertion and traps on either missing object or parent. */
    if (object == 0) return;
    audio_uart_page_43f66c(object);
    if (reference == 0) reference = audio_uart_lv_obj_parent_44dca2(object);
    if (reference == 0) return;
    uint32_t parent = audio_uart_lv_obj_parent_44dca2(object);
    if (parent == 0) return;

    int32_t parent_x = audio_uart_lv_style_pad_left_43efc6(parent, 0);
    int32_t parent_y = audio_uart_lv_style_pad_top_43f022(parent, 0);
    int32_t ref_x = audio_uart_lv_style_pad_left_43efc6(reference, 0);
    int32_t ref_y = audio_uart_lv_style_pad_top_43f022(reference, 0);
    int32_t x = 0, y = 0;
    uint32_t mode = (uint8_t)alignment;
    if (mode == 0) mode = audio_uart_lv_style_base_dir_43efba(reference, 0) == 1 ? 3u : 1u;

    switch (mode) {
    case 1: x = ref_x; y = ref_y; break;
    case 2: x = ref_x + audio_uart_lv_obj_content_width_43fe16(reference)/2 -
                  audio_uart_lv_obj_width_43fd9e(object)/2; y = ref_y; break;
    case 3: x = ref_x + audio_uart_lv_obj_content_width_43fe16(reference) -
                  audio_uart_lv_obj_width_43fd9e(object); y = ref_y; break;
    case 4: x = ref_x; y = ref_y + audio_uart_lv_obj_content_height_43fe70(reference) -
                          audio_uart_lv_obj_height_43fdda(object); break;
    case 5: x = ref_x + audio_uart_lv_obj_content_width_43fe16(reference)/2 -
                  audio_uart_lv_obj_width_43fd9e(object)/2;
            y = ref_y + audio_uart_lv_obj_content_height_43fe70(reference) -
                  audio_uart_lv_obj_height_43fdda(object); break;
    case 6: x = ref_x + audio_uart_lv_obj_content_width_43fe16(reference) -
                  audio_uart_lv_obj_width_43fd9e(object);
            y = ref_y + audio_uart_lv_obj_content_height_43fe70(reference) -
                  audio_uart_lv_obj_height_43fdda(object); break;
    case 7: x = ref_x; y = ref_y + audio_uart_lv_obj_content_height_43fe70(reference)/2 -
                         audio_uart_lv_obj_height_43fdda(object)/2; break;
    case 8: x = ref_x + audio_uart_lv_obj_content_width_43fe16(reference) -
                  audio_uart_lv_obj_width_43fd9e(object);
            y = ref_y + audio_uart_lv_obj_content_height_43fe70(reference)/2 -
                  audio_uart_lv_obj_height_43fdda(object)/2; break;
    case 9: x = ref_x + audio_uart_lv_obj_content_width_43fe16(reference)/2 -
                  audio_uart_lv_obj_width_43fd9e(object)/2;
            y = ref_y + audio_uart_lv_obj_content_height_43fe70(reference)/2 -
                  audio_uart_lv_obj_height_43fdda(object)/2; break;
    case 10: x = 0; y = -audio_uart_lv_obj_height_43fdda(object); break;
    case 11: x = audio_uart_lv_obj_width_43fd9e(reference)/2 -
                 audio_uart_lv_obj_width_43fd9e(object)/2;
             y = -audio_uart_lv_obj_height_43fdda(object); break;
    case 12: x = audio_uart_lv_obj_width_43fd9e(reference) -
                 audio_uart_lv_obj_width_43fd9e(object);
             y = -audio_uart_lv_obj_height_43fdda(object); break;
    case 13: x = 0; y = audio_uart_lv_obj_height_43fdda(reference); break;
    case 14: x = audio_uart_lv_obj_width_43fd9e(reference)/2 -
                 audio_uart_lv_obj_width_43fd9e(object)/2;
             y = audio_uart_lv_obj_height_43fdda(reference); break;
    case 15: x = audio_uart_lv_obj_width_43fd9e(reference) -
                 audio_uart_lv_obj_width_43fd9e(object);
             y = audio_uart_lv_obj_height_43fdda(reference); break;
    case 16: x = -audio_uart_lv_obj_width_43fd9e(object); y = 0; break;
    case 17: x = -audio_uart_lv_obj_width_43fd9e(object);
             y = audio_uart_lv_obj_height_43fdda(reference)/2 -
                 audio_uart_lv_obj_height_43fdda(object)/2; break;
    case 18: x = -audio_uart_lv_obj_width_43fd9e(object);
             y = audio_uart_lv_obj_height_43fdda(reference) -
                 audio_uart_lv_obj_height_43fdda(object); break;
    case 19: x = audio_uart_lv_obj_width_43fd9e(reference); y = 0; break;
    case 20: x = audio_uart_lv_obj_width_43fd9e(reference);
             y = audio_uart_lv_obj_height_43fdda(reference)/2 -
                 audio_uart_lv_obj_height_43fdda(object)/2; break;
    case 21: x = audio_uart_lv_obj_width_43fd9e(reference);
             y = audio_uart_lv_obj_height_43fdda(reference) -
                 audio_uart_lv_obj_height_43fdda(object); break;
    default: break;
    }
    int32_t dx = percent_offset(x_offset, reference, audio_uart_lv_obj_width_43fd9e);
    int32_t dy = percent_offset(y_offset, reference, audio_uart_lv_obj_height_43fdda);
    if (audio_uart_lv_style_base_dir_43efba(parent, 0) == 1)
        dx += x + *(int32_t *)(uintptr_t)(reference + 20u) -
              *(int32_t *)(uintptr_t)(parent + 20u) +
              audio_uart_lv_scroll_right_44e67a(parent) - parent_x;
    else
        dx += x + *(int32_t *)(uintptr_t)(reference + 20u) -
              *(int32_t *)(uintptr_t)(parent + 20u) +
              audio_uart_lv_scroll_left_44e586(parent) - parent_x;
    dy += y + *(int32_t *)(uintptr_t)(reference + 24u) -
          *(int32_t *)(uintptr_t)(parent + 24u) +
          audio_uart_lv_scroll_top_44e4aa(parent) - parent_y;
    audio_uart_page_4411d4(object, 1, 0);
    audio_uart_page_43f09a(object, dx, dy);
}
