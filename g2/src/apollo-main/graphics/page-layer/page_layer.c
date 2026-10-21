/* Stock page layer update at 0x44e3ca..0x44e3f7. */
#include <stdint.h>

extern void audio_uart_lv_obj_setup_layer_43e1fa(uint32_t object);

uint32_t audio_uart_page_44e3ca(uint32_t object, uint32_t layer,
                                  uint32_t unused, uint32_t saved_r3)
{
    (void)unused;
    audio_uart_lv_obj_setup_layer_43e1fa(object);
    volatile uint8_t *const obj = (volatile uint8_t *)(uintptr_t)object;
    volatile uint8_t *const inner =
        (volatile uint8_t *)(uintptr_t)*(volatile uint32_t *)(void *)(obj + 8u);
    volatile uint16_t *const flags = (volatile uint16_t *)(void *)(inner + 0x32u);
    const uint16_t old = *flags;
    if ((layer & 0xffu) != ((old >> 6) & 15u))
        *flags = (uint16_t)((old & 0xfc3fu) | ((layer & 15u) << 6));
    return saved_r3;
}
