/* Apollo page class constructor 0x49a0c0..0x49a12d and destructor
 * 0x49a150..0x49a16d. Event callback remains a separate source gate. */
#include <stdint.h>

extern void audio_uart_page_43dfa4(void *page, uint32_t mode);
extern void audio_uart_page_layout_499678(void *page, uint32_t mode);
extern void audio_uart_page_49942e(void *page, const void *style);
extern void audio_uart_lv_heap_free(void *pointer);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t value) {
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8u);
    p[2] = (uint8_t)(value >> 16u);
    p[3] = (uint8_t)(value >> 24u);
}

void audio_uart_page_class_ctor_49a0c0(const void *class_record, void *page) {
    (void)class_record;
    uint8_t *p = (uint8_t *)page;
    put32(p + 0x2cu, 0u);
    p[0x5cu] &= 0xc0u;
    put32(p + 0x34u, 0xffffffffu);
    put32(p + 0x54u, 0u);
    put32(p + 0x58u, 0u);
    put32(p + 0x38u, 0xffffffffu);
    put32(p + 0x40u, 0u);
    put32(p + 0x3cu, 0u);
    put32(p + 0x44u, 0xffffu);
    put32(p + 0x48u, 0xffffu);
    audio_uart_page_43dfa4(page, 2u);
    audio_uart_page_layout_499678(page, 0u);
    audio_uart_page_49942e(page, (const void *)(uintptr_t)0x0078dc14u);
}

void audio_uart_page_class_dtor_49a150(const void *class_record, void *page) {
    (void)class_record;
    uint8_t *p = (uint8_t *)page;
    if ((p[0x5cu] & 0x10u) == 0u)
        audio_uart_lv_heap_free((void *)(uintptr_t)get32(p + 0x2cu));
    put32(p + 0x2cu, 0u);
}
