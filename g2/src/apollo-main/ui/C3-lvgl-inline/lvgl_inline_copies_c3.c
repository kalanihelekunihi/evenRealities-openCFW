/* IAR out-of-line copies of LVGL 9.3 static-inline helpers, plus the two
 * lv_draw_rect.c task getters, firmware 2.2.6.10. Reconstructed from the stock
 * disassembly; compilation is not byte identity.
 *
 * IAR emitted each `static inline` helper of lv_obj_style.h /
 * lv_obj_style_gen.h once per translation unit that uses it. The callers are
 * hand reconstructions of those units and reference the copies by address
 * names. Every getter is one call to lv_obj_get_style_prop (stock 0x44bdea,
 * upstream lv_obj_style.c) with a fixed property id; every pad_all copy is the
 * upstream order pad_left (0x44122a), pad_right (0x441238), pad_top
 * (0x44120e), pad_bottom (0x44121c), all upstream lv_obj_style_gen.c.
 *
 * Stock ranges:
 *   lv_refr.c TU getters        0x45311a..0x453160, 0x453180..0x4531ae
 *   lv_draw_rect.c task getters 0x451c52..0x451c6e
 *   ui_onboarding_main_page TU  0x4a8560..0x4a856c (opa), 0x4a856c..0x4a85a0 (pad_all)
 *   ui_onboarding_news_page TU  0x509fdc..0x50a00e
 *   ui_onboarding_stock_page TU 0x50ca24..0x50ca58
 *   ui_msg_notif_list TU        0x54fa24..0x54fa58
 *   menu_page_ui TU             0x460128..0x46015c */
#include <stdint.h>

/* lv_style_value_t is a 4-byte union returned in r0. */
extern uint32_t lv_obj_get_style_prop(const void *obj, uint32_t part, uint32_t prop);
extern void lv_obj_set_style_pad_left(void *obj, int32_t value, uint32_t selector);
extern void lv_obj_set_style_pad_right(void *obj, int32_t value, uint32_t selector);
extern void lv_obj_set_style_pad_top(void *obj, int32_t value, uint32_t selector);
extern void lv_obj_set_style_pad_bottom(void *obj, int32_t value, uint32_t selector);

/* LV_STYLE_* ids of the pinned lv_style.h. */
enum {
    C3_STYLE_OPA = 98,
    C3_STYLE_OPA_LAYERED = 99,
    C3_STYLE_BLEND_MODE = 105,
    C3_STYLE_TRANSFORM_SCALE_X = 110,
    C3_STYLE_TRANSFORM_SCALE_Y = 111,
    C3_STYLE_TRANSFORM_ROTATION = 112,
    C3_STYLE_TRANSFORM_PIVOT_X = 113,
    C3_STYLE_TRANSFORM_PIVOT_Y = 114,
    C3_STYLE_TRANSFORM_SKEW_X = 115,
    C3_STYLE_TRANSFORM_SKEW_Y = 116,
    C3_STYLE_BITMAP_MASK_SRC = 117
};

/* ---- lv_refr.c translation unit ---------------------------------------- */

/* Stock 0x0045311A (lv_obj_get_style_transform_scale_x copy) */
uint32_t audio_uart_lv_draw_style_metric_45311a(void *obj, uint32_t part)
{
    return lv_obj_get_style_prop(obj, part, C3_STYLE_TRANSFORM_SCALE_X);
}

/* Stock 0x00453124 (lv_obj_get_style_transform_scale_y copy) */
uint32_t audio_uart_lv_draw_style_metric_453124(void *obj, uint32_t part)
{
    return lv_obj_get_style_prop(obj, part, C3_STYLE_TRANSFORM_SCALE_Y);
}

/* Stock 0x0045312E (lv_obj_get_style_transform_rotation copy) */
uint32_t audio_uart_lv_draw_style_metric_45312e(void *obj, uint32_t part)
{
    return lv_obj_get_style_prop(obj, part, C3_STYLE_TRANSFORM_ROTATION);
}

/* Stock 0x00453138 (lv_obj_get_style_transform_pivot_x copy) */
uint32_t audio_uart_lv_draw_style_metric_453138(void *obj, uint32_t part)
{
    return lv_obj_get_style_prop(obj, part, C3_STYLE_TRANSFORM_PIVOT_X);
}

/* Stock 0x00453142 (lv_obj_get_style_transform_pivot_y copy) */
uint32_t audio_uart_lv_draw_style_metric_453142(void *obj, uint32_t part)
{
    return lv_obj_get_style_prop(obj, part, C3_STYLE_TRANSFORM_PIVOT_Y);
}

/* Stock 0x0045314C (lv_obj_get_style_transform_skew_x copy) */
uint32_t audio_uart_lv_draw_style_metric_45314c(void *obj, uint32_t part)
{
    return lv_obj_get_style_prop(obj, part, C3_STYLE_TRANSFORM_SKEW_X);
}

/* Stock 0x00453156 (lv_obj_get_style_transform_skew_y copy) */
uint32_t audio_uart_lv_draw_style_metric_453156(void *obj, uint32_t part)
{
    return lv_obj_get_style_prop(obj, part, C3_STYLE_TRANSFORM_SKEW_Y);
}

/* Stock 0x00453180 (lv_obj_get_style_opa copy) */
uint32_t audio_uart_lv_draw_style_metric_453180(void *obj, uint32_t part)
{
    return (uint8_t)lv_obj_get_style_prop(obj, part, C3_STYLE_OPA);
}

/* Stock 0x0045318C (lv_obj_get_style_opa_layered copy) */
uint32_t audio_uart_lv_draw_style_metric_45318c(void *obj, uint32_t part)
{
    return (uint8_t)lv_obj_get_style_prop(obj, part, C3_STYLE_OPA_LAYERED);
}

/* Stock 0x00453198 (lv_obj_get_style_blend_mode copy) */
uint32_t audio_uart_lv_draw_style_metric_453198(void *obj, uint32_t part)
{
    return (uint8_t)lv_obj_get_style_prop(obj, part, C3_STYLE_BLEND_MODE);
}

/* Stock 0x004531A4 (lv_obj_get_style_bitmap_mask_src copy) */
uint32_t audio_uart_lv_draw_style_metric_4531a4(void *obj, uint32_t part)
{
    return lv_obj_get_style_prop(obj, part, C3_STYLE_BITMAP_MASK_SRC);
}

/* ---- lv_draw_rect.c translation unit (draw core is hand-written) -------- */

/* Stock 0x00451C52 (lv_draw_task_get_fill_dsc): task->type (byte +4) is
 * LV_DRAW_TASK_TYPE_FILL (1) -> task->draw_dsc (+0x54), else NULL. */
void *lv_draw_task_get_fill_dsc(void *task)
{
    const uint8_t *t = (const uint8_t *)task;
    return t[4] == 1u ? *(void *const *)(const void *)(t + 0x54u) : (void *)0;
}

/* Stock 0x00451C60 (lv_draw_task_get_border_dsc): type LV_DRAW_TASK_TYPE_BORDER (2). */
void *lv_draw_task_get_border_dsc(void *task)
{
    const uint8_t *t = (const uint8_t *)task;
    return t[4] == 2u ? *(void *const *)(const void *)(t + 0x54u) : (void *)0;
}

/* ---- product translation units ---------------------------------------- */

static void c3_pad_all(void *obj, int32_t value, uint32_t selector)
{
    lv_obj_set_style_pad_left(obj, value, selector);
    lv_obj_set_style_pad_right(obj, value, selector);
    lv_obj_set_style_pad_top(obj, value, selector);
    lv_obj_set_style_pad_bottom(obj, value, selector);
}

/* Stock 0x004A8560 (lv_obj_get_style_opa copy, ui_onboarding_main_page.c TU) */
uint8_t ui_onboarding_main_sub_004A8560(void *obj, uint32_t part)
{
    return (uint8_t)lv_obj_get_style_prop(obj, part, C3_STYLE_OPA);
}

/* Stock 0x004A856C (lv_obj_set_style_pad_all copy, ui_onboarding_main_page.c TU) */
void ui_onboarding_main_sub_004A856C(void *obj, int32_t value, uint32_t selector)
{
    c3_pad_all(obj, value, selector);
}

/* Stock 0x00509FDC (lv_obj_set_style_pad_all copy, ui_onboarding_news_page.c TU) */
void lv_obj_set_style_pad_all_509fdc(void *obj, int32_t value, uint32_t selector)
{
    c3_pad_all(obj, value, selector);
}

/* Stock 0x0050CA24 (lv_obj_set_style_pad_all copy, ui_onboarding_stock_page.c TU) */
void ui_onboarding_stock_sub_0050CA24(void *obj, int32_t value, uint32_t selector)
{
    c3_pad_all(obj, value, selector);
}

/* Stock 0x0054FA24 (lv_obj_set_style_pad_all copy, ui_msg_notif_list.c TU) */
void lv_obj_set_style_pad_all_54fa24(void *obj, int32_t value, uint32_t selector)
{
    c3_pad_all(obj, value, selector);
}

/* Stock 0x00460128 (lv_obj_set_style_pad_all copy, menu_page_ui.c TU) */
void style_pad_all_460128(void *obj, int32_t value, uint32_t selector)
{
    c3_pad_all(obj, value, selector);
}
