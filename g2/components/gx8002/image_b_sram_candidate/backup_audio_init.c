/* SPDX-License-Identifier: MIT
 * Image-B gx_audio_in_init at 0x10005ce8, source-reduced from pinned native
 * CFG and SDK GX_AUDIO_IN_CONFIG. Real child bodies and IRQ callback remain
 * explicit contracts until their image-B source is recovered.
 */
#include <stdint.h>

typedef int32_t (*gx8002_image_b_config_callback)(void);
typedef int32_t (*gx8002_image_b_stream_callback)(uint32_t, uint32_t *);
typedef int32_t (*gx8002_image_b_event_callback)(uint32_t);

typedef struct {
    gx8002_image_b_stream_callback record_callback;
    gx8002_image_b_config_callback config_callback;
    gx8002_image_b_stream_callback update_callback;
    gx8002_image_b_event_callback engvad_callback;
    gx8002_image_b_event_callback fftvad_callback;
} gx8002_image_b_audio_config;

extern void gx8002_image_b_platform_gate_10003be8(uint32_t module, uint32_t enable);
extern void gx8002_image_b_zero_100113c4(void *destination, uint32_t value, uint32_t bytes);
extern void gx8002_image_b_audio_prepare_100051ec(void);
extern void gx8002_image_b_request_irq_10004844(
    uint32_t line, void (*handler)(void), uint32_t argument);
extern void gx8002_image_b_audio_irq_10015830(void);

#define AUDIO_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0a00000) + (offset)))
#define AUDIO_CONFIG ((volatile uint32_t *)(uintptr_t)UINT32_C(0x20017624))

static void set_bit(volatile uint32_t *word, uint32_t bit, uint32_t value)
{
    uint32_t mask = UINT32_C(1) << bit;
    *word = (*word & ~mask) | ((value != 0u) ? mask : 0u);
}

int32_t gx8002_image_b_audio_init_10005ce8(gx8002_image_b_audio_config config)
{
    volatile uint32_t *state = AUDIO_CONFIG;
    gx8002_image_b_platform_gate_10003be8(3u, 1u);
    gx8002_image_b_zero_100113c4((void *)(uintptr_t)state, 0u, 28u);
    gx8002_image_b_audio_prepare_100051ec();
    set_bit(&AUDIO_WORD(0u), 31u, 1u);
    set_bit(&AUDIO_WORD(0u), 29u, 1u);
    AUDIO_WORD(0x10cu) = 0u;

    if (config.config_callback == 0) return -1;
    state[2] = (uint32_t)(uintptr_t)config.config_callback;
    if (config.update_callback != 0)
        state[4] = (uint32_t)(uintptr_t)config.update_callback;
    if (config.record_callback != 0)
        state[3] = (uint32_t)(uintptr_t)config.record_callback;
    if (config.engvad_callback != 0)
        state[5] = (uint32_t)(uintptr_t)config.engvad_callback;
    if (config.fftvad_callback != 0)
        state[6] = (uint32_t)(uintptr_t)config.fftvad_callback;

    (void)config.config_callback();
    gx8002_image_b_request_irq_10004844(
        2u, gx8002_image_b_audio_irq_10015830, 0u);

    if (config.record_callback != 0) {
        uint32_t flags = state[1];
        if ((flags & 1u) != 0u) set_bit(&AUDIO_WORD(0x100u), 0u, 1u);
        if ((flags & 2u) != 0u) set_bit(&AUDIO_WORD(0x100u), 1u, 1u);
        if ((flags & 4u) != 0u) set_bit(&AUDIO_WORD(0x100u), 2u, 1u);
    }

    uint32_t route = state[0];
    if ((route & 1u) != 0u) {
        set_bit(&AUDIO_WORD(0x0cu), 9u, 1u);
        set_bit(&AUDIO_WORD(0u), 7u, 0u);
    }
    if ((route & 2u) != 0u) {
        if ((AUDIO_WORD(0x28u) & 0xfu) < 2u)
            set_bit(&AUDIO_WORD(0x28u), 9u, 1u);
        if ((AUDIO_WORD(0x2cu) & 0xfu) < 2u)
            set_bit(&AUDIO_WORD(0x2cu), 9u, 1u);
        set_bit(&AUDIO_WORD(0u), 15u, 0u);
    }
    if ((route & 4u) != 0u) {
        if ((AUDIO_WORD(0x48u) & 0xfu) < 8u)
            set_bit(&AUDIO_WORD(0x48u), 9u, 1u);
        if ((AUDIO_WORD(0x4cu) & 0xfu) < 8u)
            set_bit(&AUDIO_WORD(0x4cu), 9u, 1u);
        set_bit(&AUDIO_WORD(0x04u), 31u, 0u);
    }
    return 0;
}
