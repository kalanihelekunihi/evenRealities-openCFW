/* Stock button-fade callback wrapper 0x58c230 and recursive body 0x58c138. */
#include <stdint.h>

extern void audio_uart_page_44130c(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern uint32_t audio_uart_page_441068(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_lv_child_count_44ddea(uint32_t);
extern uint32_t audio_uart_lv_child_get_44dce2(uint32_t, uint32_t);
extern uint32_t audio_uart_lv_class_is_43e2d4(uint32_t, const void *);
extern void audio_uart_page_4413ce(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44140e(uint32_t, uint32_t, uint32_t);
extern const uint8_t audio_uart_image_class_756108[];
extern const uint8_t audio_uart_page_class_7561bc[];

static uint32_t channel(uint32_t from, uint32_t to, uint32_t alpha,
                        uint32_t shift) {
    const int32_t first = (int32_t)((from >> shift) & 0xffu);
    const int32_t last = (int32_t)((to >> shift) & 0xffu);
    const int32_t delta = last - first;
    const int32_t product = (int32_t)((uint32_t)delta * alpha);
    return (uint8_t)(first + product / 255);
}

void audio_terminal_button_fade_recursive_58c138(uint32_t object,
                                                   uint32_t alpha) {
    if (object == 0u)
        return;
    audio_uart_page_44130c(object, (uint8_t)alpha, 0u);
    const int32_t opacity_product = (int32_t)(0xccu * alpha);
    const uint32_t opacity = (uint32_t)(opacity_product / 255 + 0x33);
    const uint32_t dark = audio_uart_page_44104c(0x00444444u);
    const uint32_t light = audio_uart_page_44104c(0x00ffffffu);
    const uint32_t red = channel(dark, light, alpha, 16u);
    const uint32_t green = channel(dark, light, alpha, 8u);
    const uint32_t blue = channel(dark, light, alpha, 0u);
    const uint32_t blended = audio_uart_page_441068(red, green, blue);
    const uint32_t count = audio_uart_lv_child_count_44ddea(object);
    for (uint32_t index = 0; index < count; ++index) {
        const uint32_t child = audio_uart_lv_child_get_44dce2(object, index);
        if (child == 0u)
            continue;
        if (audio_uart_lv_class_is_43e2d4(child,
                                          audio_uart_image_class_756108)) {
            audio_uart_page_4413ce(child, (uint8_t)opacity, 0u);
        } else if (audio_uart_lv_class_is_43e2d4(
                       child, audio_uart_page_class_7561bc)) {
            audio_uart_page_44140e(child, blended, 0u);
        } else {
            audio_terminal_button_fade_recursive_58c138(child, alpha);
        }
    }
}

void audio_terminal_button_fade_callback_58c230(uint32_t object,
                                                 uint32_t alpha) {
    audio_terminal_button_fade_recursive_58c138(object, alpha);
}
