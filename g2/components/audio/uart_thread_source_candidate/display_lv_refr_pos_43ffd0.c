#include <stdint.h>

extern int32_t audio_uart_lv_layout_positioned_43f612(void *);
extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern int32_t audio_uart_lv_style_x_43eee2(void *, uint32_t);
extern int32_t audio_uart_lv_style_y_43eeec(void *, uint32_t);
extern int32_t audio_uart_lv_obj_content_width_43fe16(void *);
extern int32_t audio_uart_lv_obj_content_height_43fe70(void *);
extern int32_t audio_uart_lv_style_width_43eea6(void *, uint32_t);
extern int32_t audio_uart_lv_style_height_43eec4(void *, uint32_t);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern uint8_t audio_uart_lv_style_align_43eef6(void *, uint32_t);
extern uint8_t audio_uart_lv_style_base_dir_43efba(void *, uint32_t);
extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);
extern void audio_uart_lv_obj_position_440246(void *, int32_t, int32_t);

uint32_t audio_uart_lv_style_translate_x_43ef02(void *object, uint32_t selector) {
    return audio_uart_lv_style_property_44bdea(object, selector, 0x6cu);
}

uint32_t audio_uart_lv_style_translate_y_43ef0c(void *object, uint32_t selector) {
    return audio_uart_lv_style_property_44bdea(object, selector, 0x6du);
}

static int32_t percentage(uint32_t encoded, int32_t extent) {
    const uint32_t magnitude = encoded & 0x9fffffffu;
    const int32_t signed_percent = (magnitude < 0x10000000u)
        ? (int32_t)magnitude : (int32_t)(0x0fffffffu - magnitude);
    const int32_t product = (int32_t)((uint32_t)signed_percent * (uint32_t)extent);
    return product / 100;
}

static uint32_t encoded_percentage(uint32_t encoded) {
    return ((encoded & 0x60000000u) == 0x20000000u) &&
           ((int32_t)(encoded & 0x9fffffffu) < (int32_t)0x1fffffffu);
}

void audio_uart_lv_obj_refr_pos_43ffd0(void *object) {
    if (audio_uart_lv_layout_positioned_43f612(object) != 0) return;

    void *parent = audio_uart_lv_obj_parent_44dca2(object);
    uint32_t x = (uint32_t)audio_uart_lv_style_x_43eee2(object, 0u);
    uint32_t y = (uint32_t)audio_uart_lv_style_y_43eeec(object, 0u);
    if (parent == 0) {
        audio_uart_lv_obj_position_440246(object, (int32_t)x, (int32_t)y);
        return;
    }

    const int32_t content_width = audio_uart_lv_obj_content_width_43fe16(parent);
    const int32_t content_height = audio_uart_lv_obj_content_height_43fe70(parent);
    if (encoded_percentage(x)) {
        if ((uint32_t)audio_uart_lv_style_width_43eea6(parent, 0u) == 0x3fffffffu)
            x = 0u;
        else
            x = (uint32_t)percentage(x, content_width);
    }
    if (encoded_percentage(y)) {
        if ((uint32_t)audio_uart_lv_style_height_43eec4(parent, 0u) == 0x3fffffffu)
            y = 0u;
        y = (uint32_t)percentage(y, content_height);
    }

    uint32_t tx = audio_uart_lv_style_translate_x_43ef02(object, 0u);
    uint32_t ty = audio_uart_lv_style_translate_y_43ef0c(object, 0u);
    const int32_t width = audio_uart_lv_obj_width_43fd9e(object);
    const int32_t height = audio_uart_lv_obj_height_43fdda(object);
    if (encoded_percentage(tx)) tx = (uint32_t)percentage(tx, width);
    if (encoded_percentage(ty)) ty = (uint32_t)percentage(ty, height);

    int32_t out_x = (int32_t)((uint32_t)tx + x);
    int32_t out_y = (int32_t)((uint32_t)ty + y);
    uint8_t align = audio_uart_lv_style_align_43eef6(object, 0u);
    if (align == 0u)
        align = audio_uart_lv_style_base_dir_43efba(parent, 0u) == 1u ? 3u : 1u;
    if (align == 2u || align == 5u || align == 9u)
        out_x = (int32_t)((uint32_t)out_x + (uint32_t)(content_width / 2) - (uint32_t)(width / 2));
    else if (align == 3u || align == 6u || align == 8u)
        out_x = (int32_t)((uint32_t)out_x + (uint32_t)content_width - (uint32_t)width);
    if (align == 4u || align == 5u || align == 6u)
        out_y = (int32_t)((uint32_t)out_y + (uint32_t)content_height - (uint32_t)height);
    else if (align == 7u || align == 8u || align == 9u)
        out_y = (int32_t)((uint32_t)out_y + (uint32_t)(content_height / 2) - (uint32_t)(height / 2));
    audio_uart_lv_obj_position_440246(object, out_x, out_y);
}
