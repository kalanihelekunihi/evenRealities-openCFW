/* Apollo Main transition completion callback, native 0x44cc8c..0x44ccd7. */
#include <stdint.h>

extern uint32_t audio_uart_page_style_selector_44b860(uint32_t);
extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);
extern uint32_t audio_uart_page_style_resolve_44ca18(void *, uint32_t, uint8_t, void *);
extern void *audio_uart_lv_transition_style_44c72c(void *, uint32_t);
extern void audio_uart_page_style_value_482868(void *, uint32_t, uint32_t);
extern void audio_uart_page_style_refresh_44bc8c(void *, uint32_t, uint32_t);

static uint32_t rd32(const uint8_t *p) {
    uint32_t value;
    __builtin_memcpy(&value, p, 4u);
    return value;
}
static void wr32(uint8_t *p, uint32_t value) {
    __builtin_memcpy(p, &value, 4u);
}

void audio_uart_lv_transition_ready_44cc8c(void *animation) {
    uint8_t *const record = (uint8_t *)(uintptr_t)rd32((const uint8_t *)animation);
    void *const object = (void *)(uintptr_t)rd32(record);
    const uint32_t selector = rd32(record + 8u);
    const uint32_t group = audio_uart_page_style_selector_44b860(selector);
    const uint8_t property = record[4u];
    const uint32_t value = audio_uart_lv_style_property_44bdea(object, group, property);
    wr32(record + 0x0cu, value);
    record[4u] = 0u;
    audio_uart_page_style_resolve_44ca18(object, group, property, record);
    record[4u] = property;
    uint8_t *const style_entry = (uint8_t *)audio_uart_lv_transition_style_44c72c(object, selector);
    audio_uart_page_style_value_482868((void *)(uintptr_t)rd32(style_entry), property, value);
    audio_uart_page_style_refresh_44bc8c(object, selector, property);
}
