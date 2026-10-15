/* Apollo base-object style getters, native 0x43dd52..0x43dd71 and
 * 0x43de76..0x43de81. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *object,
                                                     uint32_t selector,
                                                     uint32_t property);

uint32_t audio_uart_lv_metric_43dd52(void *object, uint32_t selector) {
    return audio_uart_lv_style_property_44bdea(object, selector, 1u);
}

uint32_t audio_uart_lv_metric_43dd5c(void *object, uint32_t selector) {
    return audio_uart_lv_style_property_44bdea(object, selector, 2u);
}

uint32_t audio_uart_lv_metric_43dd66(void *object, uint32_t selector) {
    return (uint8_t)audio_uart_lv_style_property_44bdea(object, selector, 0xau);
}

uint32_t audio_uart_lv_metric_43de76(void *object, uint32_t selector) {
    return (uint16_t)audio_uart_lv_style_property_44bdea(object, selector, 0x16u);
}
