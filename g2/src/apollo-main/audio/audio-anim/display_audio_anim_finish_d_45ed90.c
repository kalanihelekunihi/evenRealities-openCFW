/* Apollo audio animation completion callback, stock 0x45ed90..0x45ee32. */
#include <stdint.h>

extern void audio_uart_display_audio_finalize(void);
extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern void audio_uart_display_audio_queue_45f58c(void *);
extern void audio_uart_display_audio_dispatch_45fd06(void *);

static uint32_t load32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

static void store32(uint8_t *p, uint32_t value) {
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8u);
    p[2] = (uint8_t)(value >> 16u);
    p[3] = (uint8_t)(value >> 24u);
}

/* Stock 0x0045ED90 (page anim completion callback) */
void audio_uart_display_anim_finish_d_45ed91(void *descriptor) {
    uint8_t *page = (uint8_t *)(uintptr_t)load32((const uint8_t *)descriptor);
    uint8_t *entry = (uint8_t *)(uintptr_t)load32(page + 16u);
    entry[28] = 0u;
    audio_uart_display_audio_finalize();

    uint8_t *parent = (uint8_t *)audio_uart_lv_obj_parent_44dca2(page);
    while (parent != 0 && load32(parent + 16u) == 0u)
        parent = (uint8_t *)audio_uart_lv_obj_parent_44dca2(parent);
    uint8_t *owner = (uint8_t *)(uintptr_t)load32(parent + 16u);
    if (owner == 0) return;

    if (load32(owner + 16u) != 0u) {
        store32(owner + 16u, 0u);
        owner[20] = 0u;
        audio_uart_display_audio_queue_45f58c(owner);
    } else {
        owner[20] = 0u;
        uint8_t *current = (uint8_t *)(uintptr_t)load32(owner + 12u);
        while (current != 0 && current[28] != 1u)
            current = (uint8_t *)(uintptr_t)load32(current + 32u);
        if (current != 0) {
            uint32_t callback = load32(current + 24u);
            if (callback != 0u)
                ((void (*)(void *, void *, uint32_t, uint32_t))(uintptr_t)callback)(
                    current, owner, 0x43u, 0u);
            store32(owner + 4u, (uint32_t)(uintptr_t)current);
            callback = load32(entry + 24u);
            if (callback != 0u)
                ((void (*)(void *, void *, uint32_t, uint32_t))(uintptr_t)callback)(
                    entry, owner, 0x4eu, 0u);
        }
    }
    owner[0xe8u] = 0u;
    audio_uart_display_audio_dispatch_45fd06(owner);
}
