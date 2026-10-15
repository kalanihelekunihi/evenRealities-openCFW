/* Apollo page metric selectors called by class event 0x49a16e. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *page,
                                                     uint32_t selector,
                                                     uint32_t property);

int32_t audio_uart_page_metric_499360(void *page, uint32_t selector) {
    return (int32_t)audio_uart_lv_style_property_44bdea(page, selector, 1u);
}
int32_t audio_uart_page_metric_49936a(void *page, uint32_t selector) {
    return (int32_t)audio_uart_lv_style_property_44bdea(page, selector, 5u);
}
int32_t audio_uart_page_metric_499374(void *page, uint32_t selector) {
    return (int32_t)audio_uart_lv_style_property_44bdea(page, selector, 7u);
}
const uint8_t *audio_uart_page_metric_4993c0(void *page, uint32_t selector) {
    return (const uint8_t *)(uintptr_t)audio_uart_lv_style_property_44bdea(
            page, selector, 0x5au);
}
int32_t audio_uart_page_metric_4993ca(void *page, uint32_t selector) {
    return (int32_t)audio_uart_lv_style_property_44bdea(page, selector, 0x5bu);
}
int32_t audio_uart_page_metric_4993d4(void *page, uint32_t selector) {
    return (int32_t)audio_uart_lv_style_property_44bdea(page, selector, 0x5cu);
}
