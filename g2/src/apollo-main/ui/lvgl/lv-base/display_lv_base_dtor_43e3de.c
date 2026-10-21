/* Apollo base object destructor, native 0x43e3de..0x43e441. */
#include <stdint.h>

extern void audio_uart_lv_style_mark_45028e(void *object);
extern void audio_uart_page_lock_44bde0(uint32_t value);
extern void audio_uart_lv_theme_refresh_44bc3a(void *object);
extern uint32_t audio_uart_lv_style_unlink_450500(void *object, void *style);
extern void *audio_uart_lv_obj_group_43e1be(void *object);
extern void audio_uart_page_unlink_44d3b2(void *object);
extern void audio_uart_lv_style_destroy_450228(void *list);
extern void audio_uart_lv_heap_free(void *object);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

static void put32(uint8_t *p, uint32_t value) {
    p[0] = (uint8_t)value; p[1] = (uint8_t)(value >> 8u);
    p[2] = (uint8_t)(value >> 16u); p[3] = (uint8_t)(value >> 24u);
}

void audio_uart_lv_base_dtor_43e3de(void *unused, void *object) {
    (void)unused;
    uint8_t *page = (uint8_t *)object;
    audio_uart_lv_style_mark_45028e(page);
    audio_uart_page_lock_44bde0(0u);
    audio_uart_lv_theme_refresh_44bc3a(page);
    audio_uart_page_lock_44bde0(1u);
    (void)audio_uart_lv_style_unlink_450500(page, 0);
    if (audio_uart_lv_obj_group_43e1be(page) != 0)
        audio_uart_page_unlink_44d3b2(page);
    uint32_t spec_address = get32(page + 8u);
    if (spec_address != 0u) {
        uint8_t *spec = (uint8_t *)(uintptr_t)spec_address;
        uint32_t first = get32(spec);
        if (first != 0u) {
            audio_uart_lv_heap_free((void *)(uintptr_t)first);
            put32(spec, 0u);
        }
        audio_uart_lv_style_destroy_450228(spec + 8u);
        audio_uart_lv_heap_free(spec);
        put32(page + 8u, 0u);
    }
}
