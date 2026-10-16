/* Stock Terminal row update at 0x5ea768. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern uint32_t audio_terminal_item_59737c(uint32_t item_index);
extern void audio_lv_object_flag_43ded4(uint32_t object, uint32_t flag);
extern void audio_lv_object_position_43f09a(uint32_t object, uint32_t x, uint32_t y);
extern void audio_lv_object_size_call_43f4c0(uint32_t object, uint32_t width, uint32_t height);
extern void audio_terminal_row_bind_5ea564(uint32_t object, uint32_t item, uint32_t item_index);
extern void audio_lv_object_clear_flag_43dfa4(uint32_t object, uint32_t flag);

void audio_terminal_view_row_5ea768(uint32_t slot, uint32_t item_index) {
    uint8_t *state = audio_terminal_ui_state_base;
    if (slot >= 12u)
        return;
    uint32_t object = *(const uint32_t *)(const void *)(state + 0xcu + slot * 4u);
    if (object == 0u)
        return;
    uint16_t index = (uint16_t)item_index;
    uint32_t item = audio_terminal_item_59737c(index);
    if (item == 0u) {
        audio_lv_object_flag_43ded4(object, 1u);
        return;
    }
    uint32_t offset = *(const uint32_t *)(const void *)(state + 0xbcu + (uint32_t)index * 4u);
    uint16_t height = *(const uint16_t *)(const void *)(state + 0x3cu + (uint32_t)index * 2u);
    if (height < 0x1cu)
        height = 0x1cu;
    audio_lv_object_position_43f09a(object, 0u, offset);
    audio_lv_object_size_call_43f4c0(object, 0x240u, height);
    audio_terminal_row_bind_5ea564(object, item, index);
    audio_lv_object_clear_flag_43dfa4(object, 1u);
}
