/* Style-property wrappers called by Apollo base event-state 0x43e442. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);

#define METRIC(address, property) \
    uint32_t audio_uart_lv_event_state_metric_##address(void *object, uint32_t selector) { \
        return audio_uart_lv_style_property_44bdea(object, selector, property); \
    }
#define BYTE_METRIC(address, property) \
    uint32_t audio_uart_lv_event_state_metric_##address(void *object, uint32_t selector) { \
        return (uint8_t)audio_uart_lv_style_property_44bdea(object, selector, property); \
    }

METRIC(43de4a, 0x0cu)
METRIC(43dd72, 0x6au)
METRIC(43dd7c, 0x6bu)
METRIC(43ddd8, 0x26u)
BYTE_METRIC(43dda8, 0x1du)
BYTE_METRIC(43de6a, 0x62u)
BYTE_METRIC(43ddb4, 0x20u)
BYTE_METRIC(43ddcc, 0x25u)
BYTE_METRIC(43ddc0, 0x24u)

uint32_t audio_uart_lv_event_state_metric_43de54(void *object, uint32_t selector) {
    return audio_uart_lv_style_property_44bdea(object, selector, 0x2du) != 0u;
}
