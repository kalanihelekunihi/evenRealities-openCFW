/* Apollo Main Conversate list-slot opacity callbacks and fade scheduler. */
#include <stdint.h>

extern uint32_t audio_terminal_ui_object_valid_43e2ea(uint32_t);
extern uint32_t audio_uart_lv_style_unlink_450500(void *, void *);
extern void audio_lv_style_opa_441488(uint32_t, uint32_t, uint32_t);
extern void audio_uart_lv_anim_init_4503d6(void *);
extern void audio_uart_lv_anim_values_4506ce(void *, int32_t, int32_t);
extern void *audio_uart_lv_anim_start_450408(void *);
extern void audio_uart_lv_anim_path_450688(void);

void audio_conversate_list_slot_opacity_callback_5b0c4e(uint32_t object,
                                                          uint32_t alpha) {
    if (object != 0u && audio_terminal_ui_object_valid_43e2ea(object) != 0u)
        audio_lv_style_opa_441488(object, (uint8_t)alpha, 0u);
}

void audio_conversate_list_slot_alpha_5b0c72(uint32_t object, uint32_t alpha) {
    if (object == 0u || audio_terminal_ui_object_valid_43e2ea(object) == 0u)
        return;
    (void)audio_uart_lv_style_unlink_450500(
        (void *)(uintptr_t)object,
        (void *)(uintptr_t)&audio_conversate_list_slot_opacity_callback_5b0c4e);
    audio_lv_style_opa_441488(object, (uint8_t)alpha, 0u);
}

static void put_word(uint8_t *bytes, uint32_t offset, uint32_t value) {
    *(uint32_t *)(void *)(bytes + offset) = value;
}

void audio_conversate_list_slot_fade_5b0ca0(
    uint32_t object, uint32_t first, uint32_t last,
    uint32_t delay, uint32_t duration) {
    if (object == 0u || audio_terminal_ui_object_valid_43e2ea(object) == 0u)
        return;
    (void)audio_uart_lv_style_unlink_450500(
        (void *)(uintptr_t)object,
        (void *)(uintptr_t)&audio_conversate_list_slot_opacity_callback_5b0c4e);
    audio_lv_style_opa_441488(object, (uint8_t)first, 0u);
    uint8_t descriptor[0x60];
    audio_uart_lv_anim_init_4503d6(descriptor);
    put_word(descriptor, 0u, object);
    audio_uart_lv_anim_values_4506ce(descriptor, (uint8_t)first, (uint8_t)last);
    put_word(descriptor, 0x34u, (uint32_t)(0u - delay));
    put_word(descriptor, 0x30u, duration);
    put_word(descriptor, 0x20u, (uint32_t)(uintptr_t)&audio_uart_lv_anim_path_450688);
    put_word(descriptor, 4u,
             (uint32_t)(uintptr_t)&audio_conversate_list_slot_opacity_callback_5b0c4e);
    (void)audio_uart_lv_anim_start_450408(descriptor);
}
