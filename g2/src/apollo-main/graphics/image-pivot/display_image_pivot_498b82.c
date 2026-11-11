/* Apollo image pivot getter 0x498b82..0x498bc8 and LVGL coordinate
 * percentage decoder 0x451600..0x45163a (upstream lv_pct_to_px). */
#include <stdint.h>

extern void lv_log_add(uint32_t, const char *, uint32_t,
    const char *, const char *, ...);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t value) {
    p[0] = (uint8_t)value; p[1] = (uint8_t)(value >> 8u);
    p[2] = (uint8_t)(value >> 16u); p[3] = (uint8_t)(value >> 24u);
}

/* 0x451600 is upstream lv_pct_to_px (third-party/upstream/lvgl/src/misc/lv_area.c). */
extern int32_t lv_pct_to_px(int32_t v, int32_t base);

void audio_uart_lv_image_get_pivot_498b82(void *object, void *output) {
    if (object == 0) {
        lv_log_add(3u,
            "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\widgets\\image\\lv_image.c",
            0x1fcu, "lv_image_get_pivot",
            "Asserted at expression: %s (%s)", "obj != NULL", "NULL pointer");
        for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    }
    const uint8_t *image = (const uint8_t *)object;
    uint8_t *point = (uint8_t *)output;
    put32(point, (uint32_t)lv_pct_to_px(
        (int32_t)get32(image + 0x50u), (int32_t)get32(image + 0x3cu)));
    put32(point + 4u, (uint32_t)lv_pct_to_px(
        (int32_t)get32(image + 0x54u), (int32_t)get32(image + 0x40u)));
}
