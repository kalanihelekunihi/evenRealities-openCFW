/* Apollo Main LVGL area overlap 0x450f00 and object extra draw size
 * 0x452dc8, used by the render-area selector. */
#include <stdint.h>

uint32_t audio_uart_lv_area_overlap_450f00(const void *first,
                                             const void *second)
{
    const int32_t *const a = (const int32_t *)first;
    const int32_t *const b = (const int32_t *)second;
    return (uint32_t)(b[2] >= a[0] && a[2] >= b[0] &&
                      b[3] >= a[1] && a[3] >= b[1]);
}

uint32_t audio_uart_lv_obj_ext_draw_size_452dc8(void *object)
{
    const uint8_t *const bytes = (const uint8_t *)object;
    const uint32_t spec = *(const uint32_t *)(const void *)(bytes + 8u);
    if (spec == 0u) return 0u;
    return *(const uint32_t *)(uintptr_t)(spec + 0x2cu);
}
