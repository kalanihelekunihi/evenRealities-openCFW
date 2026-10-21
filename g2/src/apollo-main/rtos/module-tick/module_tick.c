/* TinyFrame instance feed and timer pump, native 0x491b9a and 0x492288. */
#include <stdint.h>

extern void audio_uart_module_feed_byte(void *module, uint8_t value); /* 0x491be4 */
extern void audio_uart_module_timer_expire(void *module, uint32_t slot,
                                            void *timer); /* 0x49183e */

void audio_uart_module_receive(void *module, const void *bytes,
                               uint32_t count) {
    const uint8_t *input = (const uint8_t *)bytes;
    for (uint32_t i = 0; i < count; ++i)
        audio_uart_module_feed_byte(module, input[i]);
}

void audio_uart_module_pump(void *module) {
    uint8_t *base = (uint8_t *)module;
    uint16_t *tick = (uint16_t *)(base + 0x12u);
    if (*tick < 100u) *tick = (uint16_t)(*tick + 1u);
    for (uint32_t slot = 0; slot < base[0x7158u]; ++slot) {
        uint8_t *timer = base + 0x6430u + slot * 0x18u;
        uint32_t active = *(uint32_t *)(timer + 4u);
        uint16_t *remaining = (uint16_t *)(timer + 12u);
        if (active != 0u && *remaining != 0u) {
            --*remaining;
            if (*remaining == 0u) {
                void (*callback)(void *, uint32_t) =
                    *(void (**)(void *, uint32_t))(timer + 8u);
                if (callback != 0)
                    callback(module, *(uint32_t *)(timer + 20u));
                audio_uart_module_timer_expire(module, slot, timer);
            }
        }
    }
}
