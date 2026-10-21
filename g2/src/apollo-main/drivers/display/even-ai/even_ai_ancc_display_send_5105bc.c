/* Stock ANCC callback-list dispatcher, 0x5105bc. */
#include <stdint.h>

/* Head pointer and enable byte are observed at 0x20073f84..0x20073f88. */
uint8_t g2_audio_ancc_display_context_20073f84[8];

static uint32_t word(const void *base, uint32_t offset) {
    return *(const uint32_t *)((const uint8_t *)base + offset);
}

void audio_even_ai_ancc_display_send_5105bc(void *context, uint32_t value,
                                               const uint32_t *count) {
    if (!context || !word(context, 0u) || !((const uint8_t *)context)[4u])
        return;
    const uint8_t *node = (const uint8_t *)(uintptr_t)word(context, 0u);
    while (node) {
        uint32_t address = word(node, 0u);
        if (address)
            ((void (*)(uint32_t, const uint32_t *))(uintptr_t)address)(value, count);
        node = (const uint8_t *)(uintptr_t)word(node, 4u);
    }
}
