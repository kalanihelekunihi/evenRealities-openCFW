/* Apollo object relative X/Y getters, stock 0x43fc70..0x43fd3e. */
#include <stdint.h>

extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern int32_t audio_uart_lv_obj_x_44e486(void *);
extern int32_t audio_uart_lv_obj_y_44e498(void *);
extern int32_t audio_uart_lv_style_pad_left_43efc6(void *, uint32_t);
extern int32_t audio_uart_lv_style_pad_top_43f022(void *, uint32_t);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

int32_t audio_uart_lv_obj_x_43fc70(void *object) {
    const uint8_t *o = (const uint8_t *)object;
    void *parent = audio_uart_lv_obj_parent_44dca2(object);
    uint32_t result = get32(o + 20u);
    if (parent != 0) {
        result -= get32((const uint8_t *)parent + 20u);
        result += (uint32_t)audio_uart_lv_obj_x_44e486(parent);
        result -= (uint32_t)audio_uart_lv_style_pad_left_43efc6(parent, 0u);
    }
    return (int32_t)result;
}

int32_t audio_uart_lv_obj_y_43fce0(void *object) {
    const uint8_t *o = (const uint8_t *)object;
    void *parent = audio_uart_lv_obj_parent_44dca2(object);
    uint32_t result = get32(o + 24u);
    if (parent != 0) {
        result -= get32((const uint8_t *)parent + 24u);
        result += (uint32_t)audio_uart_lv_obj_y_44e498(parent);
        result -= (uint32_t)audio_uart_lv_style_pad_top_43f022(parent, 0u);
    }
    return (int32_t)result;
}
