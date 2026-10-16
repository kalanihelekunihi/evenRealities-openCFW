#include <stdint.h>

extern uint8_t audio_uart_display_lv_state[];
extern void audio_uart_lv_list_remove_482c0e(void *, void *);
extern void audio_uart_lv_transition_schedule_4509da(void);
extern void audio_uart_lv_heap_free(void *);

static uint32_t word(const uint8_t *p, uint32_t at) {
    return *(const uint32_t *)(const void *)(p + at);
}
static void store(uint8_t *p, uint32_t at, uint32_t value) {
    *(uint32_t *)(void *)(p + at) = value;
}

void audio_uart_lv_anim_remove_450910(void *animation) {
    uint8_t *const anim = (uint8_t *)animation;
    const uint32_t reverse = (anim[0x5cu] >> 1) & 1u;
    const uint32_t repeat_count = word(anim, 0x44u);
    if (reverse == 0u && repeat_count != 0u && repeat_count != 0xffffffffu)
        store(anim, 0x44u, repeat_count - 1u);

    if (word(anim, 0x44u) == 0u &&
        (word(anim, 0x3cu) == 0u || reverse != 0u)) {
        audio_uart_lv_list_remove_482c0e(audio_uart_display_lv_state + 0xacu, anim);
        audio_uart_lv_transition_schedule_4509da();
        if (word(anim, 0x10u) != 0u)
            ((void (*)(void *))(uintptr_t)word(anim, 0x10u))(anim);
        if (word(anim, 0x14u) != 0u)
            ((void (*)(void *))(uintptr_t)word(anim, 0x14u))(anim);
        audio_uart_lv_heap_free(anim);
        return;
    }

    uint32_t overrun = 0u;
    if ((int32_t)word(anim, 0x30u) < (int32_t)word(anim, 0x34u))
        overrun = word(anim, 0x34u) - word(anim, 0x30u);
    store(anim, 0x34u, overrun - word(anim, 0x40u));
    if (word(anim, 0x3cu) != 0u) {
        if (reverse == 0u)
            store(anim, 0x34u, 0u - word(anim, 0x38u));
        anim[0x5cu] ^= 2u;
        uint32_t temporary = word(anim, 0x24u);
        store(anim, 0x24u, word(anim, 0x2cu));
        store(anim, 0x2cu, temporary);
        temporary = word(anim, 0x30u);
        store(anim, 0x30u, word(anim, 0x3cu));
        store(anim, 0x3cu, temporary);
    }
}
