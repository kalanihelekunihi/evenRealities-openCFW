#include <stdint.h>

extern uint8_t audio_uart_display_lv_state[]; /* stock RAM 0x2006f548 */
extern void *audio_uart_lv_list_first(void *);
extern void *audio_uart_lv_list_next(void *, void *);
extern uint32_t audio_uart_lv_elapsed(uint32_t);
extern uint32_t audio_uart_lv_tick(void);
extern void audio_uart_lv_anim_normalize_450a3e(void *);
extern void audio_uart_lv_anim_cancel_matching_450a74(void *);
extern void audio_uart_lv_anim_remove_450910(void *);

static uint32_t word(const uint8_t *bytes, uint32_t offset) {
    return *(const uint32_t *)(const void *)(bytes + offset);
}
static void store(uint8_t *bytes, uint32_t offset, uint32_t value) {
    *(uint32_t *)(void *)(bytes + offset) = value;
}

void audio_uart_lv_transition_timer_callback_450758(void *timer) {
    (void)timer;
    uint8_t *const state = audio_uart_display_lv_state;
    state[0xa5u] = state[0xa5u] == 0u ? 1u : 0u;
    void *const list = state + 0xacu;
    uint8_t *anim = (uint8_t *)audio_uart_lv_list_first(list);
    while (anim != 0) {
        const uint32_t elapsed = audio_uart_lv_elapsed(word(anim, 0x50u));
        if ((anim[0x5cu] & 1u) != 0u) {
            const uint32_t delay_elapsed = audio_uart_lv_elapsed(word(anim, 0x54u));
            const uint32_t start = word(anim, 0x58u);
            if (start != 0xffffffffu && delay_elapsed >= start) {
                anim[0x5cu] &= (uint8_t)~1u;
                store(anim, 0x34u, word(anim, 0x34u) + delay_elapsed - start);
                anim[0x5cu] = (uint8_t)((anim[0x5cu] & ~4u) |
                                        ((state[0xa5u] == 0u ? 1u : 0u) << 2));
            }
        } else {
            store(anim, 0x34u, word(anim, 0x34u) + elapsed);
        }
        store(anim, 0x50u, audio_uart_lv_tick());
        state[0xa4u] = 0u;

        if ((anim[0x5cu] & 1u) == 0u &&
            ((anim[0x5cu] >> 2) & 1u) != state[0xa5u]) {
            anim[0x5cu] = (uint8_t)((anim[0x5cu] & ~4u) |
                                    ((state[0xa5u] & 1u) << 2));
            if ((anim[0x5cu] & 8u) == 0u && (int32_t)word(anim, 0x34u) >= 0) {
                if ((anim[0x5cu] & 0x10u) == 0u && word(anim, 0x18u) != 0u) {
                    const int32_t shift = ((int32_t (*)(void *))(uintptr_t)word(anim, 0x18u))(anim);
                    store(anim, 0x24u, word(anim, 0x24u) + (uint32_t)shift);
                    store(anim, 0x2cu, word(anim, 0x2cu) + (uint32_t)shift);
                }
                audio_uart_lv_anim_normalize_450a3e(anim);
                if (word(anim, 0x0cu) != 0u)
                    ((void (*)(void *))(uintptr_t)word(anim, 0x0cu))(anim);
                anim[0x5cu] |= 8u;
                audio_uart_lv_anim_cancel_matching_450a74(anim);
            }
            if ((int32_t)word(anim, 0x34u) >= 0) {
                const uint32_t original = word(anim, 0x34u);
                const int32_t duration = (int32_t)word(anim, 0x30u);
                if (duration < (int32_t)original)
                    store(anim, 0x34u, (uint32_t)duration);
                const uint32_t clipped = word(anim, 0x34u);
                const uint32_t value = ((uint32_t (*)(void *))(uintptr_t)word(anim, 0x20u))(anim);
                if (value != word(anim, 0x28u)) {
                    store(anim, 0x28u, value);
                    if (word(anim, 4u) != 0u)
                        ((void (*)(void *, uint32_t))(uintptr_t)word(anim, 4u))(
                            (void *)(uintptr_t)word(anim, 0u), value);
                    if (state[0xa4u] == 0u && word(anim, 8u) != 0u)
                        ((void (*)(void *, uint32_t))(uintptr_t)word(anim, 8u))(anim, value);
                }
                if (state[0xa4u] == 0u) {
                    if (word(anim, 0x34u) == clipped)
                        store(anim, 0x34u, original);
                    if (duration <= (int32_t)word(anim, 0x34u))
                        audio_uart_lv_anim_remove_450910(anim);
                }
            }
        }
        if (state[0xa4u] == 0u)
            anim = (uint8_t *)audio_uart_lv_list_next(list, anim);
        else
            anim = (uint8_t *)audio_uart_lv_list_first(list);
    }
}
