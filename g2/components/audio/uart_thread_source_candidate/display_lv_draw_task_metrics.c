/* Apollo draw-task style accessors, native 0x4522e8..0x452615.
 * The eight compass accessors in this span are source-owned elsewhere. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);

#define RAW(address, property) \
    uint32_t audio_uart_lv_draw_metric_##address(void *object, uint32_t selector) { \
        return audio_uart_lv_style_property_44bdea(object, selector, property); \
    }
#define BYTE(address, property) \
    uint32_t audio_uart_lv_draw_metric_##address(void *object, uint32_t selector) { \
        return (uint8_t)audio_uart_lv_style_property_44bdea(object, selector, property); \
    }
#define BOOL(address, property) \
    uint32_t audio_uart_lv_draw_metric_##address(void *object, uint32_t selector) { \
        return audio_uart_lv_style_property_44bdea(object, selector, property) != 0u; \
    }

RAW(4522e8, 0x1cu)
BYTE(452308, 0x1du)
RAW(452314, 0x23u)
BYTE(452334, 0x20u)
RAW(452340, 0x21u)
RAW(45234a, 0x22u)
BYTE(452354, 0x24u)
BYTE(452360, 0x25u)
RAW(45236c, 0x26u)
RAW(452376, 0x28u)
BYTE(452380, 0x29u)
RAW(45238c, 0x2au)
BYTE(4523ac, 0x2bu)
BOOL(4523b8, 0x2cu)
RAW(4523ce, 0x31u)
BYTE(4523ee, 0x32u)
RAW(4523fa, 0x30u)
BYTE(452404, 0x34u)
RAW(45241a, 0x39u)
RAW(452478, 0x3du)
BYTE(4524a4, 0x44u)
RAW(4524b0, 0x45u)
BYTE(4524d0, 0x46u)
RAW(4524dc, 0x48u)
RAW(4524e6, 0x49u)
RAW(4524f0, 0x4au)
BOOL(4524fa, 0x4bu)
RAW(452510, 0x4cu)
BYTE(452530, 0x4du)
RAW(45253c, 0x50u)
BOOL(452546, 0x51u)
RAW(45255c, 0x52u)
BYTE(45257c, 0x53u)
RAW(452588, 0x54u)
RAW(452592, 0x58u)
BYTE(4525b2, 0x59u)
RAW(4525be, 0x5au)
RAW(4525c8, 0x5bu)
RAW(4525d2, 0x5cu)
BYTE(4525dc, 0x5du)
BYTE(4525e8, 0x5eu)
RAW(4525f4, 0x0cu)
BYTE(45260a, 0x69u)
