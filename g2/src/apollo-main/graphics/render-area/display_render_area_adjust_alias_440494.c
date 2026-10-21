/* Refresh render-area spelling for the already sourced native 0x440494 body. */
#include <stdint.h>

extern void audio_uart_lv_object_scrollbar_area_440494(void *, int32_t *,
                                                       uint32_t);

void audio_uart_lv_obj_adjust_area_440494(void *object, void *area,
                                           uint32_t flags)
{
    audio_uart_lv_object_scrollbar_area_440494(object, (int32_t *)area, flags);
}
