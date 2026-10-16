/* Apollo Main transition deletion callback, native 0x44ccd8..0x44cd9d. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[]; /* RAM 0x2006f548 */
extern void *audio_uart_lv_list_first(void *);
extern void *audio_uart_lv_list_next(void *, void *);
extern void audio_uart_lv_list_remove_482c0e(void *, void *);
extern void audio_uart_lv_heap_free(void *);
extern uint32_t audio_uart_lv_style_notify_4827b0(void *, uint32_t);
extern void audio_uart_lv_style_remove_44ba9a(void *, void *, uint32_t);

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

void audio_uart_lv_transition_delete_44ccd8(void *animation) {
    uint8_t *const node = (uint8_t *)(uintptr_t)rd32((const uint8_t *)animation);
    uint8_t *const object = (uint8_t *)(uintptr_t)rd32(node);
    const uint8_t property = node[4u];
    void *const root = audio_uart_display_lv_root + 0x18u;
    for (uint8_t *other = (uint8_t *)audio_uart_lv_list_first(root);
         other != 0; other = (uint8_t *)audio_uart_lv_list_next(root, other)) {
        if (other != node && rd32(other) == rd32(node) &&
            rd32(other + 8u) == rd32(node + 8u) && other[4u] == property)
            return;
    }
    const uint32_t count = (rd16(object + 0x2au) & 0x03ffu) >> 4u;
    uint8_t *const styles = (uint8_t *)(uintptr_t)rd32(object + 0x0cu);
    for (uint32_t i = 0; i < count; ++i) {
        uint8_t *const record = styles + i * 8u;
        const uint32_t selector = rd32(record + 4u);
        if ((selector & 0x02000000u) == 0u ||
            (selector & 0x00ffffffu) != rd32(node + 8u))
            continue;
        audio_uart_lv_list_remove_482c0e(root, node);
        audio_uart_lv_heap_free(node);
        void *const style = (void *)(uintptr_t)rd32(record);
        audio_uart_lv_style_notify_4827b0(style, property);
        if (((const uint8_t *)style)[8u] == 0u)
            audio_uart_lv_style_remove_44ba9a(object, style, selector & 0x00ffffffu);
        return;
    }
}
