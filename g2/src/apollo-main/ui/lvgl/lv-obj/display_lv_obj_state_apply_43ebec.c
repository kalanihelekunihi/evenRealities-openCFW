/* Apollo LV object state transition and bounded style refresh, native 0x43ebec..0x43ee2b. */
#include <stdint.h>

extern uint32_t audio_uart_lv_state_transition_kind_44c178(void *object,
    uint32_t previous, uint32_t next);
extern void audio_uart_display_size_changed(void *object);
extern void audio_uart_lv_update_layer_44c50e(void *object);
extern void *audio_uart_lv_heap_alloc(uint32_t bytes);
extern void audio_uart_lv_heap_free(void *pointer);
extern uint32_t audio_uart_lv_style_reference_43dce0(void *style,
    uint32_t property, void *result);
extern void audio_uart_lv_state_property_refresh_44bfae(void *object,
    uint32_t property, uint32_t previous, uint32_t next, void *entry);
extern void audio_uart_page_style_refresh_44bc8c(void *object,
    uint32_t selector, uint32_t property);
extern void audio_uart_lv_refresh_draw_452d42(void *object);

static uint16_t rd16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8u));
}
static uint32_t rd32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void wr16(uint8_t *p, uint16_t value) {
    p[0] = (uint8_t)value; p[1] = (uint8_t)(value >> 8u);
}
static void wr32(uint8_t *p, uint32_t value) {
    for (unsigned i = 0; i < 4u; ++i) p[i] = (uint8_t)(value >> (8u * i));
}

void audio_uart_lv_obj_state_apply_43ebec(void *object, uint32_t next) {
    uint8_t *o = (uint8_t *)object;
    uint16_t previous = rd16(o + 0x28u);
    if (previous == (uint16_t)next) return;
    uint32_t kind = (uint8_t)audio_uart_lv_state_transition_kind_44c178(
        object, previous, next & 0xffffu);
    if (kind == 0u) {
        wr16(o + 0x28u, (uint16_t)next);
        return;
    }
    audio_uart_display_size_changed(object);
    wr16(o + 0x28u, (uint16_t)next);
    audio_uart_lv_update_layer_44c50e(object);
    uint8_t *scratch = (uint8_t *)audio_uart_lv_heap_alloc(0x280u);
    uint32_t count = 0u;
    uint32_t style_count = (rd16(o + 0x2au) & 0x03ffu) >> 4u;
    for (uint32_t i = 0u; i < style_count && count < 32u; ++i) {
        uint8_t *record = (uint8_t *)(uintptr_t)rd32(o + 0x0cu) + i * 8u;
        uint32_t raw = rd32(record + 4u);
        uint32_t key = raw & 0x00ffffffu;
        uint16_t selector = (uint16_t)key;
        uint32_t property = key & 0x00ff0000u;
        if ((selector & ~(uint16_t)next) != 0u || (raw & 0x02000000u) != 0u)
            continue;
        uint8_t *definition = (void *)0;
        if (audio_uart_lv_style_reference_43dce0(
                (void *)(uintptr_t)rd32(record), 0x68u, &definition) != 1u)
            continue;
        const char *letters = (const char *)(uintptr_t)rd32(definition);
        for (uint32_t j = 0u; letters[j] != 0 && count < 32u; ++j) {
            uint32_t k = 0u;
            for (; k < count; ++k) {
                uint8_t *old = scratch + k * 0x14u;
                uint32_t old_key = rd32(old + 4u);
                if (old[8] == (uint8_t)letters[j] &&
                    (old_key & 0x00ff0000u) == property &&
                    selector <= (uint16_t)old_key)
                    break;
            }
            if (k != count) continue;
            uint8_t *entry = scratch + count * 0x14u;
            wr16(entry, rd16(definition + 0x0cu));
            wr16(entry + 2u, rd16(definition + 0x10u));
            wr32(entry + 0x0cu, rd32(definition + 8u));
            entry[8] = (uint8_t)letters[j];
            wr32(entry + 0x10u, rd32(definition + 4u));
            wr32(entry + 4u, key);
            ++count;
        }
    }
    for (uint32_t i = 0u; i < count; ++i) {
        uint8_t *entry = scratch + i * 0x14u;
        audio_uart_lv_state_property_refresh_44bfae(object,
            rd32(entry + 4u) & 0x00ff0000u, previous, next & 0xffffu, entry);
    }
    audio_uart_lv_heap_free(scratch);
    if (kind == 1u || kind == 3u)
        audio_uart_page_style_refresh_44bc8c(object, 0x000f0000u, 0xffu);
    else if (kind == 2u) {
        audio_uart_display_size_changed(object);
        audio_uart_lv_refresh_draw_452d42(object);
    }
}
