/* LVGL lv_obj_set_size/width/height and size-style setters in Apollo Main. */
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

static void invalid_object(uint32_t line, const char *function) {
    audio_uart_lvgl_log(3u, path, line, function,
                        asserted, expression, reason);
    for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
}

void audio_uart_page_441164(uint32_t object, uint32_t value,
                            uint32_t selector) {
    audio_uart_page_style_apply_44be4c((void *)(uintptr_t)object, 1u,
                                        value, selector);
}

void audio_uart_page_44118e(uint32_t object, uint32_t value,
                            uint32_t selector) {
    audio_uart_page_style_apply_44be4c((void *)(uintptr_t)object, 2u,
                                        value, selector);
}

void audio_uart_page_43f506(uint32_t object, uint32_t width) {
    if (object == 0u) invalid_object(0xdfu, "lv_obj_set_width");
    uint32_t current;
    uint8_t status = (uint8_t)audio_uart_page_style_get_44beaa(object, 1u,
                                                                  &current, 0u);
    if (status == 0u || (status == 1u && current != width))
        audio_uart_page_441164(object, width, 0u);
}

void audio_uart_page_43f568(uint32_t object, uint32_t height) {
    if (object == 0u) invalid_object(0xecu, "lv_obj_set_height");
    uint32_t current;
    uint8_t status = (uint8_t)audio_uart_page_style_get_44beaa(object, 2u,
                                                                  &current, 0u);
    if (status == 0u || (status == 1u && current != height))
        audio_uart_page_44118e(object, height, 0u);
}

void audio_uart_page_43f4c0(uint32_t object, uint32_t width,
                            uint32_t height) {
    if (object == 0u) invalid_object(0xd7u, "lv_obj_set_size");
    audio_uart_page_43f506(object, width);
    audio_uart_page_43f568(object, height);
}
