/* Apollo LV state-change refresh classification, native 0x44c178..0x44c447. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_reference_43dce0(void *style,
    uint32_t property, void *result);

static uint16_t rd16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8u));
}
static uint32_t rd32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

uint32_t audio_uart_lv_state_transition_kind_44c178(void *object,
                                                       uint32_t previous,
                                                       uint32_t next) {
    static const uint8_t geometry[] = {
        0x10,0x11,0x12,0x13,0x15,0x14,0x16,0x6c,0x6d,
        0x01,0x02,0x04,0x05,0x06,0x07,0x30
    };
    static const uint8_t layout[] = {
        0x6a,0x6b,0x70,0x6e,0x6f,0x3a,0x3b,
        0x38,0x3c,0x3e,0x40,0x41,0x42,0x48
    };
    const uint8_t *o = (const uint8_t *)object;
    uint32_t count = (rd16(o + 0x2au) & 0x03ffu) >> 4u;
    uint8_t result = 0u;
    for (uint32_t i = 0; i < count; ++i) {
        const uint8_t *record = (const uint8_t *)(uintptr_t)rd32(o + 0x0cu) + i * 8u;
        uint32_t raw = rd32(record + 4u);
        if ((raw & 0x02000000u) != 0u) continue;
        uint16_t selector = (uint16_t)(raw & 0x00ffffffu);
        uint8_t was_active = (selector & ~(uint16_t)previous) == 0u;
        uint8_t now_active = (selector & ~(uint16_t)next) == 0u;
        if (was_active == now_active) continue;
        void *style = (void *)(uintptr_t)rd32(record);
        uint32_t value = next;
        for (unsigned j = 0; j < sizeof(geometry); ++j)
            if (audio_uart_lv_style_reference_43dce0(style, geometry[j], &value) != 0u)
                return 3u;
        uint8_t layout_found = 0u;
        for (unsigned j = 0; j < sizeof(layout); ++j) {
            if (audio_uart_lv_style_reference_43dce0(style, layout[j], &value) != 0u) {
                layout_found = 1u;
                break;
            }
        }
        if (layout_found) result = 2u;
        else if (result == 0u) result = 1u;
    }
    return result;
}
