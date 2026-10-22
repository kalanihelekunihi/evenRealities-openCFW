/* Native red-black tree remove 0x5c3600, including transplant and successor. */
#include <stdint.h>
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_font_rb_fix_remove(void *,void *,void *); /* 0x5c3976 */
static uint32_t get(const void *node,uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)((const uint8_t *)node+offset);
}
/* Stock 0x5C379C (lv_rb_minimum_from loop label inside 0x5C3798; upstream third-party/upstream/lvgl/src/misc/lv_rb.c) */
/* Stock 0x5C379A (FUN_005c379c; loop-body label inside lv_rb_minimum_from 0x5C3798, not a separate function) */
void *audio_uart_lv_cache_rb_leftmost_5c3798(void *node) { /* native 0x5c3798 */
    uint8_t *n=(uint8_t *)node;
    while(get(n,4u)!=0u) n=(uint8_t *)(uintptr_t)get(n,4u);
    return n;
}
