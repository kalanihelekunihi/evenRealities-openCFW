/* Native LVGL flex next-item helper 0x48c770. The direction is byte-width. */
#include <stdint.h>

void *audio_uart_lv_flex_next_item_48c770(void *object, uint32_t reverse, int32_t *index)
{
    uint8_t *spec = *(uint8_t **)((uint8_t *)object + 8u);
    uint32_t *children = *(uint32_t **)(void *)spec;
    int32_t next = *index + ((uint8_t)reverse ? -1 : 1);
    *index = next;
    if ((uint8_t)reverse ? next < 0 : next >= (int32_t)*(uint16_t *)(void *)(spec + 0x30u))
        return 0;
    return (void *)(uintptr_t)children[next];
}
