/* Style-property wrappers called by Apollo scrollbar descriptor 0x43e6a6. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);

#define METRIC(address, property) \
    uint32_t audio_uart_lv_scrollbar_metric_##address(void *object, uint32_t selector) { \
        return audio_uart_lv_style_property_44bdea(object, selector, property); \
    }
#define BYTE_METRIC(address, property) \
    uint32_t audio_uart_lv_scrollbar_metric_##address(void *object, uint32_t selector) { \
        return (uint8_t)audio_uart_lv_style_property_44bdea(object, selector, property); \
    }

METRIC(43dd9a, 0x1cu)
BYTE_METRIC(43ddf0, 0x32u)
METRIC(43dde2, 0x31u)
BYTE_METRIC(43de3e, 0x3eu)
METRIC(43de1c, 0x3cu)
METRIC(43de26, 0x42u)
METRIC(43de30, 0x3du)
