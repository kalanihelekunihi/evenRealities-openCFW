/* Apollo LVGL image transform setters: rotation 0x4988dc, pivot 0x498a14,
 * scale_update 0x4991e0. Source flow follows pinned LVGL v9.3 lv_image.c. */
#include <stdint.h>

extern void audio_uart_page_43f66c(void *);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern void audio_uart_lv_image_get_pivot_498b82(void *, void *);
extern void audio_uart_ambiq_transform_area_488cda(void *, int32_t, int32_t,
    int32_t, int32_t, int32_t, const void *);
extern void audio_uart_lv_invalidate_area_4405d4(void *, const void *);
extern void *audio_uart_lv_display_for_object(void *);
extern void audio_uart_lv_display_invalidation_44fe8e(void *, uint32_t);
extern void audio_uart_lv_refresh_draw_452d42(void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
    const char *, const char *, ...);

static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\widgets\\image\\lv_image.c";
static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t value) {
    p[0] = (uint8_t)value; p[1] = (uint8_t)(value >> 8u);
    p[2] = (uint8_t)(value >> 16u); p[3] = (uint8_t)(value >> 24u);
}
static void require_object(void *object, uint32_t line, const char *function) {
    if (object != 0) return;
    audio_uart_lvgl_log(3u, path, line, function,
        "Asserted at expression: %s (%s)", "obj != NULL", "NULL pointer");
    for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
}
static void invalidated_transformed(void *object, int32_t width, int32_t height,
                                    const int32_t pivot[2], uint32_t margin) {
    uint8_t *image = (uint8_t *)object;
    int32_t area[4];
    audio_uart_ambiq_transform_area_488cda(area, width, height,
        (int32_t)get32(image + 0x44u),
        (int32_t)(uint16_t)get32(image + 0x48u),
        (int32_t)(uint16_t)get32(image + 0x4cu), pivot);
    int32_t x = (int32_t)get32(image + 20u);
    int32_t y = (int32_t)get32(image + 24u);
    area[0] += x - (int32_t)margin;
    area[1] += y - (int32_t)margin;
    area[2] += x + (int32_t)margin;
    area[3] += y + (int32_t)margin;
    audio_uart_lv_invalidate_area_4405d4(object, area);
}
static void refresh_without_invalidation(void *object) {
    void *display = audio_uart_lv_display_for_object(object);
    audio_uart_lv_display_invalidation_44fe8e(display, 0u);
    audio_uart_lv_refresh_draw_452d42(object);
    audio_uart_lv_display_invalidation_44fe8e(display, 1u);
}

void audio_uart_lv_image_set_rotation_4988dc(void *object, int32_t angle) {
    require_object(object, 0x119u, "lv_image_set_rotation");
    uint8_t *image = (uint8_t *)object;
    if (((get32(image + 0x58u) >> 8u) & 0xfu) >= 11u) angle = 0;
    else {
        while (angle >= 3600) angle -= 3600;
        while (angle < 0) angle += 3600;
    }
    if ((uint32_t)angle == get32(image + 0x44u)) return;
    audio_uart_page_43f66c(object);
    int32_t width = audio_uart_lv_obj_width_43fd9e(object);
    int32_t height = audio_uart_lv_obj_height_43fdda(object);
    int32_t pivot[2];
    audio_uart_lv_image_get_pivot_498b82(object, pivot);
    invalidated_transformed(object, width, height, pivot, 0u);
    put32(image + 0x44u, (uint32_t)angle);
    refresh_without_invalidation(object);
    invalidated_transformed(object, width, height, pivot, 0u);
}

void audio_uart_lv_image_set_pivot_498a14(void *object, int32_t x, int32_t y) {
    require_object(object, 0x146u, "lv_image_set_pivot");
    uint8_t *image = (uint8_t *)object;
    if (((get32(image + 0x58u) >> 8u) & 0xfu) >= 11u) { x = 0; y = 0; }
    if (get32(image + 0x50u) == (uint32_t)x &&
        get32(image + 0x54u) == (uint32_t)y) return;
    audio_uart_page_43f66c(object);
    int32_t width = audio_uart_lv_obj_width_43fd9e(object);
    int32_t height = audio_uart_lv_obj_height_43fdda(object);
    int32_t pivot[2];
    audio_uart_lv_image_get_pivot_498b82(object, pivot);
    invalidated_transformed(object, width, height, pivot, 0u);
    put32(image + 0x50u, (uint32_t)x);
    put32(image + 0x54u, (uint32_t)y);
    refresh_without_invalidation(object);
    audio_uart_lv_image_get_pivot_498b82(object, pivot);
    invalidated_transformed(object, width, height, pivot, 0u);
}

void audio_uart_lv_image_scale_update_4991e0(void *object,
                                              int32_t scale_x, int32_t scale_y) {
    uint8_t *image = (uint8_t *)object;
    audio_uart_page_43f66c(object);
    int32_t width = audio_uart_lv_obj_width_43fd9e(object);
    int32_t height = audio_uart_lv_obj_height_43fdda(object);
    int32_t pivot[2];
    audio_uart_lv_image_get_pivot_498b82(object, pivot);
    invalidated_transformed(object, width, height, pivot, 1u);
    put32(image + 0x48u, (uint32_t)scale_x);
    put32(image + 0x4cu, (uint32_t)scale_y);
    refresh_without_invalidation(object);
    invalidated_transformed(object, width, height, pivot, 1u);
}
