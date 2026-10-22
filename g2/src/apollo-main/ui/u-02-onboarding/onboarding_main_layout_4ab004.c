/* Onboarding main page layout helper, native 0x4AB004..0x4AB061 (literal
 * pool shared with the page code up to 0x4ABC03).
 *
 * The TSV module "LVGL/src/core/lv_obj_pos.c" is a call-topology guess: this
 * is product UI code that only calls lv_obj_pos.c APIs. It is called seven
 * times from ui_onboarding_main_sub_004AA270 (0x4AA35E..0x4AA95C) with the
 * current onboarding step. Step 11 sizes one label to the space left of a
 * 471-px row and pins a second object to the bottom-right corner; every other
 * step lets the label size to its content and centres the second object at
 * the bottom. */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void);                 /* 0x45a568 */
extern int32_t audio_uart_lv_obj_width_43fd9e(void *object);      /* lv_obj_get_width */
extern void audio_lv_width_43f506(void *object, int32_t width);   /* lv_obj_set_width */
extern void lv_obj_align_43f6b8(void *object, uint8_t align,
                                int32_t x_offset, int32_t y_offset); /* lv_obj_align */

extern void *g2_onboarding_main_obj_20074d60; /* RAM 0x20074D60, width reference */
extern void *g2_onboarding_main_obj_20074d08; /* RAM 0x20074D08, resized label */
extern void *g2_onboarding_main_obj_20074cfc; /* RAM 0x20074CFC, aligned object */

#define G2_LV_ALIGN_BOTTOM_MID   5u
#define G2_LV_ALIGN_BOTTOM_RIGHT 6u
#define G2_LV_SIZE_CONTENT       0x3FFFFFFF /* LV_COORD_SET_SPEC(LV_COORD_MAX) */
#define G2_ONBOARDING_ROW_WIDTH  471

void ui_onboarding_main_layout_4ab004(uint8_t step)
{
    (void)audio_uart_device_role_get(); /* result unused in stock */

    if (step == 11u) {
        int32_t used = audio_uart_lv_obj_width_43fd9e(g2_onboarding_main_obj_20074d60);
        audio_lv_width_43f506(g2_onboarding_main_obj_20074d08, G2_ONBOARDING_ROW_WIDTH - used);
        lv_obj_align_43f6b8(g2_onboarding_main_obj_20074cfc, G2_LV_ALIGN_BOTTOM_RIGHT, -8, -16);
    } else {
        audio_lv_width_43f506(g2_onboarding_main_obj_20074d08, G2_LV_SIZE_CONTENT);
        lv_obj_align_43f6b8(g2_onboarding_main_obj_20074cfc, G2_LV_ALIGN_BOTTOM_MID, 0, -16);
    }
}
