/* LVGL lv_obj_set_x/y at 0x43f0e0/0x43f142 and their style setters. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, ...);
extern uint32_t audio_uart_page_style_get_44beaa(uint32_t, uint32_t,
                                                  uint32_t *, uint32_t);
extern void audio_uart_page_style_apply_44be4c(void *, uint8_t,
                                                uint32_t, uint32_t);

static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_pos.c";
static const char asserted[] = "Asserted at expression: %s (%s)";
static const char expression[] = "obj != NULL";
static const char reason[] = "NULL pointer";

void audio_uart_page_4411b8(uint32_t object, uint32_t value,
                            uint32_t selector) {
    audio_uart_page_style_apply_44be4c((void *)(uintptr_t)object, 8u,
                                        value, selector);
}

void audio_uart_page_4411c6(uint32_t object, uint32_t value,
                            uint32_t selector) {
    audio_uart_page_style_apply_44be4c((void *)(uintptr_t)object, 9u,
                                        value, selector);
}

void audio_uart_page_43f0e0(uint32_t object, uint32_t x) {
    if (object == 0u) {
        audio_uart_lvgl_log(3u, path, 0x3du, "lv_obj_set_x",
                            asserted, expression, reason);
        for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    }
    uint32_t current;
    uint8_t status = (uint8_t)audio_uart_page_style_get_44beaa(object, 8u,
                                                                  &current, 0u);
    if (status == 0u || (status == 1u && current != x))
        audio_uart_page_4411b8(object, x, 0u);
}

void audio_uart_page_43f142(uint32_t object, uint32_t y) {
    if (object == 0u) {
        audio_uart_lvgl_log(3u, path, 0x4bu, "lv_obj_set_y",
                            asserted, expression, reason);
        for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    }
    uint32_t current;
    uint8_t status = (uint8_t)audio_uart_page_style_get_44beaa(object, 9u,
                                                                  &current, 0u);
    if (status == 0u || (status == 1u && current != y))
        audio_uart_page_4411c6(object, y, 0u);
}
