/* Native LV layout ID selector 0x4546d0 and callback dispatch 0x4546f4. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[]; /* native RAM 0x2006f548 */
extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t,
                                                     uint32_t);

uint32_t audio_uart_lv_layout_id_4546d0(void *object, uint32_t selector) {
    return (uint16_t)audio_uart_lv_style_property_44bdea(object, selector,
                                                           0x16u);
}

void audio_uart_lv_obj_layout_apply_4546f4(void *object) {
    uint8_t id = (uint8_t)audio_uart_lv_layout_id_4546d0(object, 0u);
    if (id == 0u) return;
    uint32_t maximum = *(const uint32_t *)(const void *)(audio_uart_display_lv_root + 0x58u);
    if (id > maximum) return;
    const uint8_t *table = *(const uint8_t *const *)(const void *)(audio_uart_display_lv_root + 0x5cu);
    const uint8_t *row = table + (uint32_t)id * 8u;
    void (*callback)(void *, uint32_t) =
        *(void (**)(void *, uint32_t))(const void *)row;
    uint32_t argument = *(const uint32_t *)(const void *)(row + 4u);
    callback(object, argument);
}
