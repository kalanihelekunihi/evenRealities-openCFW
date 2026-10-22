/* Apollo audio animation finish callback, stock 0x45ed4e..0x45ed8e. */
#include <stdint.h>

extern void *audio_uart_display_audio_find_owner_45fcd2(void *);
extern void audio_uart_display_audio_finalize(void);
extern void audio_uart_display_audio_dispatch_45fd06(void *);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

/* Stock 0x0045ED4E (page anim finish callback) */
void audio_uart_display_anim_finish_b_45ed4f(void *descriptor) {
    uint8_t *page = (uint8_t *)(uintptr_t)get32((const uint8_t *)descriptor);
    uint8_t *entry = (uint8_t *)(uintptr_t)get32(page + 16u);
    entry[28] = 1u;
    uint8_t *owner = (uint8_t *)audio_uart_display_audio_find_owner_45fcd2(page);
    uint32_t callback = get32(entry + 24u);
    if (callback != 0u) {
        ((void (*)(void *, void *, uint32_t, uint32_t))(uintptr_t)callback)(
            entry, owner, 0x4du, 0u);
    }
    audio_uart_display_audio_finalize();
    if (owner != 0) {
        owner[0xe8u] = 0u;
        audio_uart_display_audio_dispatch_45fd06(owner);
    }
}
