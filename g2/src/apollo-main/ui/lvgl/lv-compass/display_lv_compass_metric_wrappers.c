/* Style-property wrappers called by Apollo extent 0x452c66. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);

#define METRIC(address, property) \
    int32_t audio_uart_lv_compass_part_##address(void *object, uint32_t selector) { \
        return (int32_t)audio_uart_lv_style_property_44bdea(object, selector, property); \
    }
#define BYTE_METRIC(address, property) \
    uint32_t audio_uart_lv_compass_part_##address(void *object, uint32_t selector) { \
        return (uint8_t)audio_uart_lv_style_property_44bdea(object, selector, property); \
    }

METRIC(4522d4, 0x6au)
METRIC(4522de, 0x6bu)
METRIC(452410, 0x38u)
BYTE_METRIC(45243a, 0x3au)
METRIC(452446, 0x3bu)
METRIC(452450, 0x3cu)
METRIC(45245a, 0x40u)
METRIC(452464, 0x41u)
METRIC(45246e, 0x42u)
BYTE_METRIC(452498, 0x3eu)
