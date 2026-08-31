/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_core_provider.h"

_Static_assert(sizeof(void *) == 4, "G2 pointer ABI changed");
_Static_assert(sizeof(lv_area_t) == 16, "lv_area_t ABI changed");
_Static_assert(sizeof(lv_matrix_t) == 36, "lv_matrix_t ABI changed");
_Static_assert(sizeof(lv_color_format_t) == 1, "lv_color_format_t enum ABI changed");
_Static_assert(sizeof(lv_event_code_t) == 4, "lv_event_code_t enum ABI changed");

void open_cfw_lvgl_core_provider_abi_probe(void)
{
    void (*area_set)(lv_area_t *, int32_t, int32_t, int32_t, int32_t) = lv_area_set;
    int32_t (*area_width)(const lv_area_t *) = lv_area_get_width;
    bool (*area_intersect)(lv_area_t *, const lv_area_t *, const lv_area_t *) = lv_area_intersect;
    uint8_t (*format_bpp)(lv_color_format_t) = lv_color_format_get_bpp;
    lv_event_code_t (*event_code)(lv_event_t *) = lv_event_get_code;
    void (*translate)(lv_matrix_t *, float, float) = lv_matrix_translate;
    void (*transform)(const lv_matrix_t *, lv_fpoint_t *) = lv_matrix_transform_point;

    (void)area_set;
    (void)area_width;
    (void)area_intersect;
    (void)format_bpp;
    (void)event_code;
    (void)translate;
    (void)transform;
}
