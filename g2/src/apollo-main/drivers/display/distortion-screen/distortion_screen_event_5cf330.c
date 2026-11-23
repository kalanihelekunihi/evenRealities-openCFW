/* Reconstructed semantic_pdt_distortion_screen_event at 0x005cf330.
 * The page calls are separate providers; the ROM assets and RAM placement
 * named below still need source ownership before a whole-image link. */
#include <stdint.h>
#include "distortion_screen_assets.h"

extern uint32_t audio_uart_page_43de82(uint32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern void audio_uart_page_43f09a(uint32_t, int32_t, int32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f506(uint32_t, uint32_t);
extern void audio_uart_page_43f568(uint32_t, uint32_t);
extern void audio_uart_page_43ded4(uint32_t, uint32_t);
extern void audio_uart_page_43f6b8(uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void lv_obj_set_style_pad_top(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_pad_bottom(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_pad_left(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_pad_right(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441246(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441254(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44127e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_4412ec(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44130c(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_border_width(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_outline_width(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_outline_pad(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_shadow_width(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_shadow_offset_x(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_shadow_offset_y(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_shadow_spread(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44140e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44142e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44143e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44145a(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_radius(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_48ba78(uint32_t, uint32_t);
extern void audio_uart_page_48ba92(uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_page_498668(uint32_t);
extern void audio_uart_page_498680(uint32_t, const void *);
extern uint32_t audio_uart_page_499416(uint32_t);
extern void audio_uart_page_49942e(uint32_t, const char *);
extern uint32_t audio_uart_page_460084(const void *);
extern const char *audio_uart_page_45fffe(const char *, uint32_t);
/* The stock literal points at the ring-list primary head cell. */
extern uint32_t audio_uart_ring_primary_head_cell;
extern uint32_t audio_uart_registry_context_20003064[];

/* Stock calls the out-of-line pad_all copy at 0x5cf2b4 with (object, 0, 0);
 * it is defined once, in ui/p-16-pdt-screens/pdt_screen_helpers.c. */
extern void semantic_zero_four_object_styles(uint32_t object, uint32_t value, uint32_t selector);

/* Stock 0x5cf32c..0x5cf32f (movs r0,#1; bx lr): input handler stored at
 * +0x18 of the page's UI-registry context (RAM 0x20003064, word 0x5cf32d). */
uint32_t semantic_distortion_predicate_true_5cf32c(uint32_t arg0, uint32_t arg1,
                                                   uint32_t code, const uint8_t *event) {
    (void)arg0;
    (void)arg1;
    (void)code;
    (void)event;
    return 1u;
}

uint32_t audio_uart_registry_callback_5cf330(uint32_t event, uint32_t arg2,
                                              uint32_t value, uint32_t parent) {
    (void)arg2;
    (void)value;
    if (event != 2u) return 0;
    uint32_t root = audio_uart_page_43de82(parent);
    audio_uart_distortion_root_2007487c = root;
    audio_uart_page_43dfa4(root, 0x10);
    audio_uart_page_43f506(root, 0x280);
    audio_uart_page_43f568(root, 0x1e0);
    audio_uart_page_44127e(root, audio_uart_page_44104c(0), 0);
    audio_uart_page_44129e(root, 0xff, 0);
    lv_obj_set_style_border_width(root, 0, 0);
    semantic_zero_four_object_styles(root, 0, 0);

    uint32_t top = audio_uart_page_43de82(root);
    audio_uart_page_43dfa4(top, 0x10);
    audio_uart_page_43f09a(top, 0, 0x32);
    audio_uart_page_43f506(top, 0x23e);
    audio_uart_page_43f568(top, 0xce);
    audio_uart_page_44127e(top, audio_uart_page_44104c(0), 0);
    audio_uart_page_44129e(top, 0, 0);
    lv_obj_set_style_border_width(top, 2, 0);
    audio_uart_page_4412ec(top, audio_uart_page_44104c(0xffffff), 0);
    audio_uart_page_44130c(top, 0xff, 0);
    lv_obj_set_style_outline_width(top, 0, 0);
    lv_obj_set_style_outline_pad(top, 0, 0);
    lv_obj_set_style_shadow_width(top, 0, 0);
    lv_obj_set_style_shadow_spread(top, 0, 0);
    lv_obj_set_style_shadow_offset_x(top, 0, 0);
    lv_obj_set_style_shadow_offset_y(top, 0, 0);
    semantic_zero_four_object_styles(top, 0, 0);
    lv_obj_set_style_pad_top(top, 0, 0);
    lv_obj_set_style_pad_bottom(top, 0, 0);
    lv_obj_set_style_pad_left(top, 0, 0);
    lv_obj_set_style_pad_right(top, 0, 0);
    lv_obj_set_style_radius(top, 0, 0);
    audio_uart_page_44140e(top, audio_uart_page_44104c(0xffffff), 0);
    audio_uart_page_44142e(top, 0xff, 0);

    uint32_t center = audio_uart_page_43de82(top);
    audio_uart_page_43f4c0(center, 0x3fffffff, 0x3fffffff);
    audio_uart_page_44129e(center, 0, 0);
    lv_obj_set_style_border_width(center, 0, 0);
    semantic_zero_four_object_styles(center, 0, 0);
    audio_uart_page_48ba78(center, 1);
    audio_uart_page_48ba92(center, 2, 2, 2);
    audio_uart_page_441246(center, 8, 0);
    audio_uart_page_43f6b8(center, 9, 0, 0);

    uint32_t child = audio_uart_page_43de82(center);
    audio_uart_page_43f4c0(child, 0x3fffffff, 0x3fffffff);
    audio_uart_page_44129e(child, 0, 0);
    lv_obj_set_style_border_width(child, 0, 0);
    semantic_zero_four_object_styles(child, 0, 0);
    audio_uart_page_48ba78(child, 0);
    audio_uart_page_48ba92(child, 2, 2, 2);
    audio_uart_page_441254(child, 8, 0);
    uint32_t icon = audio_uart_page_498668(child);
    audio_uart_page_498680(icon, &audio_uart_distortion_asset_769f58);
    audio_uart_page_43f506(icon, 0x18);
    audio_uart_page_43f568(icon, 0x18);
    audio_uart_page_43ded4(icon, 0x10000);
    audio_uart_page_43dfa4(icon, 0x10);

    uint32_t label = audio_uart_page_499416(child);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffff), 0);
    audio_uart_page_49942e(label, audio_uart_page_45fffe(
        (const char *)audio_uart_distortion_text_736af4,
        audio_uart_page_460084(audio_uart_distortion_text_736af4)));
    audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0);
    label = audio_uart_page_499416(center);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffff), 0);
    audio_uart_page_49942e(label, audio_uart_page_45fffe(
        (const char *)audio_uart_distortion_text_736b24,
        audio_uart_page_460084(audio_uart_distortion_text_736b24)));
    audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0);
    audio_uart_page_44145a(label, 2, 0);
    audio_uart_registry_context_20003064[1] = root;
    return 0;
}
