/* Stock Terminal reset prelude at 0x5e51ba. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_terminal_reset_preclear_5e7f26(void);
extern uint32_t audio_terminal_reset_mode_notice_54f50e(uint32_t mode);
extern void audio_terminal_processing_hide_5e4878(uint32_t object);
extern void audio_terminal_ui_stop_service_b_5ec268(void);
extern void audio_terminal_ui_stop_service_c_5ebbc6(void);
extern void audio_terminal_ui_stop_service_d_5ec770(void);
extern void audio_terminal_ui_stop_service_e_5ec9c0(void);
extern void audio_terminal_ui_stop_service_a_5eceb2(void);
extern void audio_terminal_processing_prepare_5ea30c(void);
extern void audio_terminal_reset_ancillary_5e65f8(void);
extern void audio_terminal_reset_display_5e4c84(uint32_t enabled);
extern void audio_lv_obj_invalidate_43dfa4(uint32_t object, uint32_t value);

void audio_terminal_reset_first_5e51ba(uint32_t old_state) {
    uint8_t *state = audio_terminal_ui_state_base;
    audio_terminal_reset_preclear_5e7f26();
    if ((uint8_t)old_state == 4u) {
        (void)audio_terminal_reset_mode_notice_54f50e(6u);
        audio_terminal_processing_hide_5e4878(
            *(uint32_t *)(void *)(state + 0x1f8u));
    }
    audio_terminal_ui_stop_service_b_5ec268();
    audio_terminal_ui_stop_service_c_5ebbc6();
    audio_terminal_ui_stop_service_d_5ec770();
    audio_terminal_ui_stop_service_e_5ec9c0();
    audio_terminal_ui_stop_service_a_5eceb2();
    audio_terminal_processing_prepare_5ea30c();
    audio_terminal_reset_ancillary_5e65f8();
    state[0x280u] = 0u;
    *(uint32_t *)(void *)(state + 0x284u) = 0u;
    audio_terminal_reset_display_5e4c84(0u);
    uint32_t root = *(uint32_t *)(void *)state;
    if (root != 0u)
        audio_lv_obj_invalidate_43dfa4(root, 1u);
}
