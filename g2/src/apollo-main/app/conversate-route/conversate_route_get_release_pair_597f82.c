/* Native release-pair getter at 0x597f82. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t level, const char *module,
                                uint32_t line, const char *format, ...);

static const char source_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\widgets\\animimage\\lv_animimage.c";
static const char getter_name[] = "lv_animimg_get_anim";
static const char assertion[] = "Asserted at expression: %s (%s)";
static const char object_not_null[] = "obj != NULL";
static const char null_pointer[] = "NULL pointer";

uint32_t audio_conversate_route_get_release_pair_597f82(uint32_t handle) {
    if (handle == 0u) {
        audio_uart_lvgl_log(3u, source_path, 0xafu, getter_name,
                            assertion, object_not_null, null_pointer);
        for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    }
    return handle + 0x5cu;
}
