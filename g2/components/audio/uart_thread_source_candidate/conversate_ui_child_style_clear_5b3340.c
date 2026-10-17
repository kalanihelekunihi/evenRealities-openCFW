/* Native Conversate UI recursive child style clear 0x5b3340..0x5b3383. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint32_t audio_terminal_ui_object_valid_43e2ea(uint32_t);
extern uint32_t audio_uart_lv_style_unlink_450500(void *, void *);
extern uint32_t audio_lv_child_count_44ddea(uint32_t);
extern uint32_t audio_lv_child_44dce2(uint32_t, uint32_t);

void audio_conversate_ui_child_style_clear_5b3340(uint32_t object) {
    if (object == 0u || audio_terminal_ui_object_valid_43e2ea(object) == 0u)
        return;
    const volatile uint8_t *const ui =
        (const volatile uint8_t *)(uintptr_t)
        ((uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    const uint32_t exempt = *(const volatile uint32_t *)(const void *)(ui + 0x18u);
    if (object == exempt)
        return;
    (void)audio_uart_lv_style_unlink_450500((void *)(uintptr_t)object, 0);
    const uint32_t count = audio_lv_child_count_44ddea(object);
    for (uint32_t index = 0u; index < count; ++index)
        audio_conversate_ui_child_style_clear_5b3340(
            audio_lv_child_44dce2(object, index));
}
