/* Small Apollo base event-state children: 0x43dcc0, 0x43de06, 0x43ddfc. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);

void audio_uart_lv_event_area_copy_43dcc0(void *destination, const void *source) {
    uint32_t *out = (uint32_t *)destination;
    const uint32_t *in = (const uint32_t *)source;
    out[0] = in[0]; out[1] = in[1]; out[2] = in[2]; out[3] = in[3];
}

uint32_t audio_uart_lv_event_state_metric_43de06(void *object, uint32_t selector) {
    return audio_uart_lv_style_property_44bdea(object, selector, 0x35u) != 0u;
}

uint32_t audio_uart_lv_event_state_metric_43ddfc(void *object, uint32_t selector) {
    return audio_uart_lv_style_property_44bdea(object, selector, 0x30u);
}
