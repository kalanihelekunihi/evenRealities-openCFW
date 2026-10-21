/* Apollo Main draw-object style property leaves, stock 0x45311a..0x4531ae,
 * plus color-format byte width 0x441004..0x441016. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t,
                                                     uint32_t);
extern uint32_t audio_uart_lv_color_bpp_440f44(uint32_t);

#define METRIC(address, property) \
    uint32_t audio_uart_lv_draw_style_metric_##address(void *object, \
                                                        uint32_t selector) \
    { return audio_uart_lv_style_property_44bdea(object, selector, property); }
#define BYTE_METRIC(address, property) \
    uint32_t audio_uart_lv_draw_style_metric_##address(void *object, \
                                                        uint32_t selector) \
    { return (uint8_t)audio_uart_lv_style_property_44bdea(object, selector, property); }

METRIC(45311a, 0x6eu)
METRIC(453124, 0x6fu)
METRIC(45312e, 0x70u)
METRIC(453138, 0x71u)
METRIC(453142, 0x72u)
METRIC(45314c, 0x73u)
METRIC(453156, 0x74u)
METRIC(453160, 0x0cu)
BYTE_METRIC(453180, 0x62u)
BYTE_METRIC(45318c, 0x63u)
BYTE_METRIC(453198, 0x69u)
METRIC(4531a4, 0x75u)

uint32_t audio_uart_lv_draw_style_metric_45316a(void *object,
                                                  uint32_t selector)
{
    return audio_uart_lv_style_property_44bdea(object, selector, 0x2du) != 0u;
}

uint32_t audio_uart_lv_color_format_bytes_441004(uint32_t format)
{
    const uint32_t bits = audio_uart_lv_color_bpp_440f44((uint8_t)format);
    return (uint8_t)((uint16_t)(bits + 7u) >> 3u);
}
