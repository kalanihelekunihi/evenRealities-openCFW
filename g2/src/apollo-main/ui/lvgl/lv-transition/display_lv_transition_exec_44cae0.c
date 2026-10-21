/* Apollo Main animated style-value callback, native 0x44cae0..0x44cc7d.
 * The flash defaults at 0x78f270 and 0x78f274 are both zero in the
 * authenticated s200 v2.2.6.10 Main image. */
#include <stdint.h>

extern uint32_t audio_uart_lv_color_rgb_mix_482dd8(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_lv_style_get_prop_44b7ce(void *, uint32_t, uint32_t *);
extern void audio_uart_page_style_value_482868(void *, uint32_t, uint32_t);
extern void audio_uart_page_style_refresh_44bc8c(void *, uint32_t, uint32_t);

static uint16_t rd16(const uint8_t *p) {
    uint16_t value;
    __builtin_memcpy(&value, p, 2u);
    return value;
}
static uint32_t rd32(const uint8_t *p) {
    uint32_t value;
    __builtin_memcpy(&value, p, 4u);
    return value;
}

static uint32_t interpolate(uint8_t property, int32_t step,
                            uint32_t start, uint32_t end) {
    switch (property) {
    case 0x34u: case 0x35u: case 0x69u:
    case 0x5au: case 0x68u:
        return step < 0xff ? start : end;
    case 0x64u:
        if (start == 0u) return end;
        if (end == 0u) return start;
        return step < 0x80 ? start : end;
    case 0x1cu: case 0x23u: case 0x31u:
    case 0x39u: case 0x3du: case 0x45u: case 0x58u:
        if (step < 1) return start & 0x00ffffffu;
        if (step >= 0xff) return end & 0x00ffffffu;
        return audio_uart_lv_color_rgb_mix_482dd8(end & 0x00ffffffu,
                                                   start & 0x00ffffffu,
                                                   (uint8_t)step) & 0x00ffffffu;
    default:
        if (step == 0) return start;
        if (step == 0xff) return end;
        {
            const uint32_t delta = end - start;
            const uint32_t product = (uint32_t)step * delta;
            const uint32_t shifted = (product >> 8u) |
                ((product & 0x80000000u) != 0u ? 0xff000000u : 0u);
            return start + shifted;
        }
    }
}

void audio_uart_lv_transition_exec_44cae0(void *record, uint32_t step) {
    const uint8_t *const node = (const uint8_t *)record;
    void *const object = (void *)(uintptr_t)rd32(node);
    const uint32_t selector = rd32(node + 8u);
    const uint8_t property = node[4u];
    const uint8_t *const obj = (const uint8_t *)object;
    const uint32_t count = (rd16(obj + 0x2au) & 0x03ffu) >> 4u;
    const uint8_t *const styles = (const uint8_t *)(uintptr_t)rd32(obj + 0x0cu);
    for (uint32_t i = 0; i < count; ++i) {
        const uint8_t *const entry = styles + i * 8u;
        const uint32_t bits = rd32(entry + 4u);
        if ((bits & 0x02000000u) == 0u ||
            (bits & 0x00ffffffu) != selector)
            continue;
        void *const style = (void *)(uintptr_t)rd32(entry);
        const uint32_t value = interpolate(property, (int32_t)step,
                                           rd32(node + 0x0cu), rd32(node + 0x10u));
        uint32_t previous = 0u; /* native flash word 0x78f274 */
        uint8_t refresh = 1u;
        if (audio_uart_lv_style_get_prop_44b7ce(style, property, &previous) != 0u &&
            value == previous)
            refresh = 0u;
        audio_uart_page_style_value_482868(style, property, value);
        if (refresh != 0u)
            audio_uart_page_style_refresh_44bc8c(object, selector, property);
        return;
    }
}
