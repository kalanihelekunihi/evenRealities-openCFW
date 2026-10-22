/* LVGL lv_image_get_src, stock
 * D:\01_workspace\s200_ap510b_iar_git\third_party\lvgl_v9.3\LVGL\src\widgets\image\lv_image.c.
 * Native 0x498b50..0x498b81 (pool words 0x498c4c..0x498c54, 0x498eb4, 0x4991c0).
 *
 * Stock variant of upstream LVGL 344c7c31 src/widgets/image/lv_image.c: the body is
 * identical (return img->src, lv_image_t +0x2c) but the stock lv_image.c revision
 * asserts at line 472 where the pinned upstream has 475 (ambiq-lvgl: 476), so the
 * upstream TU cannot stand in for it. LV_ASSERT_OBJ expands to the NULL check only
 * (class check disabled in the recovered lv_conf). */
#include <stdint.h>
#include <stddef.h>

extern void audio_uart_lvgl_log(uint32_t level, const char *file, uint32_t line,
                                const char *function, const char *format, ...); /* 0x44d25c */

static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\widgets\\image\\lv_image.c"; /* ROM 0x6e09c4 */
static const char function_name[] = "lv_image_get_src"; /* ROM 0x780d00 */
static const char assert_format[] = "Asserted at expression: %s (%s)"; /* ROM 0x761a90 */
static const char null_expression[] = "obj != NULL"; /* ROM 0x78b348 */
static const char null_reason[] = "NULL pointer"; /* ROM 0x787480 */

const void *lv_image_get_src_498b50(void *obj)
{
    if (obj == NULL) {
        audio_uart_lvgl_log(3u, source_file, 472u, function_name, assert_format,
                            null_expression, null_reason);
        for (;;)
            *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u; /* LV_ASSERT_HANDLER */
    }
    return *(const void *const *)(const void *)((const uint8_t *)obj + 0x2cu);
}
