/* Apollo layout style metric wrappers, native 0x499402..0x499415. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *page,
                                                     uint32_t selector,
                                                     uint32_t property);

int32_t audio_uart_page_metric_499402(void *page, uint32_t selector) {
    return (int32_t)audio_uart_lv_style_property_44bdea(page, selector, 0x66u);
}

int32_t audio_uart_page_metric_49940c(void *page, uint32_t selector) {
    return (int32_t)audio_uart_lv_style_property_44bdea(page, selector, 0x67u);
}
