/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\ui_onboarding_main_page.c
 * (page create code). Native 0x4AAE38..0x4AAFFD (pad 0x4AAFFE), written from
 * the 2.2.6.10 disassembly (no inventory row). Literals: 0x4ABBA0
 * (0x20074cfc), 0x4ABBF4 (0x20074d00), 0x4ABBF8 (0x808080), 0x4ABBFC
 * (0x20074d04), 0x4AB064 (key string), 0x4AB068 (0x20074d08), 0x4ABA50
 * (font cell). The pool word 0x4AB000 (0x20074d68) is not loaded here.
 * Called from ui_onboarding_main_create_4aba58 (bl at 0x4ABB84); the tip is
 * re-laid out by the helper 0x4AB004 (ui/u-02-onboarding) and shown by
 * Onboarding_ShowTouchTips (ui/a-18-onboarding-main-page).
 * Compilation is not byte identity. */
#include <stdint.h>

#define LV_SIZE_CONTENT          0x3fffffff
#define LV_OBJ_FLAG_HIDDEN       0x1u
#define LV_OBJ_FLAG_CLICKABLE    0x2u
#define ONB_ALIGN_BOTTOM_MID     5u
#define ONB_ALIGN_LEFT_MID       7u
#define ONB_PAGE_WIDE            576 /* 0x240 */
#define ONB_ROLE_MASTER          1u

extern void *g2_onboarding_main_obj_20074cfc;          /* RAM 0x20074cfc tip container (S4 data) */
extern void *g2_onboarding_tip_frame_20074d00;         /* RAM 0x20074d00 framed tip box (onboarding_menu_data.c) */
extern void *g2_onboarding_tip_anim_image_20074d04;    /* RAM 0x20074d04 phase-0 animation image (onboarding_menu_data.c) */
extern void *g2_onboarding_main_obj_20074d08;          /* RAM 0x20074d08 tip label (S4 data) */
extern uint32_t audio_uart_ring_secondary_head_cell;   /* RAM 0x200746e0, current lv_font_t * */

/* LVGL 9.3 fork (names shared with ui/a-19-onboarding-main-create). */
extern void *audio_uart_page_43de82(void *parent);                      /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flags);          /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flags);          /* lv_obj_remove_flag */
extern void audio_uart_page_43f506(void *obj, int32_t width);           /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t height);          /* lv_obj_set_height */
extern void lv_obj_align_43f6b8(void *obj, uint8_t align, int32_t x, int32_t y); /* lv_obj_align */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                   /* lv_color_hex */
extern void audio_uart_page_441180(void *obj, int32_t v, uint32_t sel); /* max_width */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel); /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel); /* pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel); /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);   /* bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel); /* border_color */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);      /* border_width */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel); /* text_color */
extern void audio_uart_page_44143e(void *obj, uint32_t font, uint32_t sel);  /* text_font */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);      /* radius */
extern void ui_onboarding_main_sub_004A856C(void *obj, int32_t v, uint32_t sel); /* lv_obj_set_style_pad_all copy */
extern void *audio_uart_page_499416(void *parent);                      /* lv_label_create */
extern const char *audio_uart_page_49942e(void *label, const char *text); /* lv_label_set_text */

extern uint32_t display_driver_uled_mode_45a568(void);                 /* device role, 1 = master */
extern uint32_t audio_uart_page_460084(const char *key);                /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index); /* localized text */
extern int32_t onboarding_animation_init_50f8cc(void *parent, uint8_t force);
extern void *onboarding_animation_get_phase_image_50fc4e(uint8_t phase);

void ui_onboarding_main_touch_tips_create_4aae38(void *parent);

static const char s_double_tap[] = "ID_ONBOARDING_DOUBLE_TAP_TO_ACTIVATE"; /* ROM 0x7509b4 */

#define ONB_TR(key) audio_uart_page_45fffe((key), audio_uart_page_460084(key))

/* Touch-tip view: hidden bottom-centred container (side padding by device
 * role, master pads right) holding a grey-framed box with the tutorial
 * animation (phase 0 image kept) and the "double tap to activate" label
 * 36 px from its left edge. */
void ui_onboarding_main_touch_tips_create_4aae38(void *parent)
{
    uint8_t role = (uint8_t)display_driver_uled_mode_45a568();

    g2_onboarding_main_obj_20074cfc = audio_uart_page_43de82(parent);
    audio_uart_page_43f506(g2_onboarding_main_obj_20074cfc, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_onboarding_main_obj_20074cfc, LV_SIZE_CONTENT);
    audio_uart_page_441180(g2_onboarding_main_obj_20074cfc, ONB_PAGE_WIDE, 0u);
    lv_obj_align_43f6b8(g2_onboarding_main_obj_20074cfc, ONB_ALIGN_BOTTOM_MID, 0, -16);
    audio_uart_page_44127e(g2_onboarding_main_obj_20074cfc, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(g2_onboarding_main_obj_20074cfc, 0xffu, 0u);
    audio_uart_page_44131c(g2_onboarding_main_obj_20074cfc, 0, 0u);
    audio_uart_page_4412ec(g2_onboarding_main_obj_20074cfc, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44146a(g2_onboarding_main_obj_20074cfc, 6, 0u);
    ui_onboarding_main_sub_004A856C(g2_onboarding_main_obj_20074cfc, 0, 0u);
    if (role == ONB_ROLE_MASTER)
        audio_uart_page_441238(g2_onboarding_main_obj_20074cfc, 16, 0u);
    else
        audio_uart_page_44122a(g2_onboarding_main_obj_20074cfc, 16, 0u);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074cfc, LV_OBJ_FLAG_CLICKABLE);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074cfc, LV_OBJ_FLAG_HIDDEN);

    g2_onboarding_tip_frame_20074d00 = audio_uart_page_43de82(g2_onboarding_main_obj_20074cfc);
    audio_uart_page_43f506(g2_onboarding_tip_frame_20074d00, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_onboarding_tip_frame_20074d00, LV_SIZE_CONTENT);
    audio_uart_page_441180(g2_onboarding_tip_frame_20074d00, ONB_PAGE_WIDE, 0u);
    lv_obj_align_43f6b8(g2_onboarding_tip_frame_20074d00, ONB_ALIGN_BOTTOM_MID, 0, 0);
    audio_uart_page_44127e(g2_onboarding_tip_frame_20074d00, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(g2_onboarding_tip_frame_20074d00, 0xffu, 0u);
    audio_uart_page_44131c(g2_onboarding_tip_frame_20074d00, 1, 0u);
    audio_uart_page_4412ec(g2_onboarding_tip_frame_20074d00, audio_uart_page_44104c(0x808080u), 0u);
    audio_uart_page_44146a(g2_onboarding_tip_frame_20074d00, 6, 0u);
    ui_onboarding_main_sub_004A856C(g2_onboarding_tip_frame_20074d00, 12, 0u);
    audio_uart_page_43dfa4(g2_onboarding_tip_frame_20074d00, LV_OBJ_FLAG_CLICKABLE);

    (void)onboarding_animation_init_50f8cc(g2_onboarding_tip_frame_20074d00, 0u);
    g2_onboarding_tip_anim_image_20074d04 = onboarding_animation_get_phase_image_50fc4e(0u);

    g2_onboarding_main_obj_20074d08 = audio_uart_page_499416(g2_onboarding_tip_frame_20074d00);
    audio_uart_page_43f506(g2_onboarding_main_obj_20074d08, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_onboarding_main_obj_20074d08, LV_SIZE_CONTENT);
    audio_uart_page_44131c(g2_onboarding_main_obj_20074d08, 0, 0u);
    ui_onboarding_main_sub_004A856C(g2_onboarding_main_obj_20074d08, 0, 0u);
    audio_uart_page_49942e(g2_onboarding_main_obj_20074d08, ONB_TR(s_double_tap));
    audio_uart_page_44143e(g2_onboarding_main_obj_20074d08, audio_uart_ring_secondary_head_cell, 0u);
    audio_uart_page_44140e(g2_onboarding_main_obj_20074d08, audio_uart_page_44104c(0xffffffu), 0u);
    lv_obj_align_43f6b8(g2_onboarding_main_obj_20074d08, ONB_ALIGN_LEFT_MID, 36, 0);
}
