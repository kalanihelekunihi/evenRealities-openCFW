/* IAR out-of-line copies of LVGL 9.3 (344c7c31) static inlines emitted at the
 * head of D:\01_workspace\s200_ap510b_iar_git\app\gui\navigation\navigation_ui.c
 * (path ROM 0x6fb6e4, module tag "navigation.ui"). Native 0x545588..0x5455e3;
 * the navigation UI proper starts at 0x5455e4.
 *   0x545588 lv_obj_get_style_opa          (src/core/lv_obj_style_gen.h)
 *   0x545594 lv_obj_set_style_pad_all      (src/core/lv_obj_style.h)
 *   0x5455c6 lv_obj_set_style_transform_scale (src/core/lv_obj_style.h)
 * Each TU that uses them carries its own copy; this one belongs to
 * navigation_ui.c. */
#include <stdint.h>

#define LV_STYLE_OPA 98u /* 0x62 */

extern uint32_t audio_uart_lv_style_property_44bdea(void *object, uint32_t selector,
                                                    uint32_t property); /* lv_obj_get_style_prop */
extern void lv_obj_set_style_pad_top(void *obj, int32_t v, uint32_t sel); /* pad_top */
extern void lv_obj_set_style_pad_bottom(void *obj, int32_t v, uint32_t sel); /* pad_bottom */
extern void lv_obj_set_style_pad_left(void *obj, int32_t v, uint32_t sel); /* pad_left */
extern void lv_obj_set_style_pad_right(void *obj, int32_t v, uint32_t sel); /* pad_right */
extern void lv_obj_set_style_transform_scale_x_4411f2(void *obj, int32_t value, uint32_t selector);
extern void lv_obj_set_style_transform_scale_y_441200(void *obj, int32_t value, uint32_t selector);

uint8_t lv_obj_get_style_opa_545588(void *obj, uint32_t part);
void lv_obj_set_style_pad_all_545594(void *obj, int32_t value, uint32_t selector);
void lv_obj_set_style_transform_scale_5455c6(void *obj, int32_t value, uint32_t selector);

uint8_t lv_obj_get_style_opa_545588(void *obj, uint32_t part)
{
    return (uint8_t)audio_uart_lv_style_property_44bdea(obj, part, LV_STYLE_OPA);
}

void lv_obj_set_style_pad_all_545594(void *obj, int32_t value, uint32_t selector)
{
    lv_obj_set_style_pad_left(obj, value, selector);
    lv_obj_set_style_pad_right(obj, value, selector);
    lv_obj_set_style_pad_top(obj, value, selector);
    lv_obj_set_style_pad_bottom(obj, value, selector);
}

void lv_obj_set_style_transform_scale_5455c6(void *obj, int32_t value, uint32_t selector)
{
    lv_obj_set_style_transform_scale_x_4411f2(obj, value, selector);
    lv_obj_set_style_transform_scale_y_441200(obj, value, selector);
}
