/* SPDX-License-Identifier: MIT
 * Native audio hardware initializer 0x102047e4..0x1020497a.
 * Product config callback is a relocatable source function pointer.
 */
#include <stdint.h>

extern void gx8002_resident_platform_gate_25080(uint32_t, uint32_t);
extern void gx8002_xip_memset_102099cc(void *, uint32_t, uint32_t);
extern uint32_t gx8002_xip_ain_reset_10203c88(void);
extern void gx8002_resident_request_irq_2553c(uint32_t, uint32_t, uint32_t);
extern void gx8002_resident_audio_irq_25e48(void);

static volatile uint32_t *const ain =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00000);
static volatile uint32_t *const audio_state =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027330);

static void set_bit(uint32_t offset, uint32_t bit)
{
    volatile uint32_t *word = &ain[offset / 4u];
    *word = *word | (UINT32_C(1) << bit);
}

static void clear_bit(uint32_t offset, uint32_t bit)
{
    volatile uint32_t *word = &ain[offset / 4u];
    *word = *word & ~(UINT32_C(1) << bit);
}

uint32_t gx8002_xip_audio_initialize_102047e4(
    uint32_t record_callback, uint32_t config_callback,
    uint32_t event_callback, uint32_t callback4, uint32_t callback5)
{
    gx8002_resident_platform_gate_25080(3u, 1u);
    gx8002_xip_memset_102099cc((void *)audio_state, 0u, 28u);
    (void)gx8002_xip_ain_reset_10203c88();
    set_bit(0u, 31u);
    set_bit(0u, 29u);
    ain[0x10cu / 4u] = 0u;
    if (config_callback == 0u) return UINT32_MAX;

    audio_state[2] = config_callback;
    if (event_callback != 0u) audio_state[4] = event_callback;
    if (record_callback != 0u) audio_state[3] = record_callback;
    if (callback4 != 0u) audio_state[5] = callback4;
    if (callback5 != 0u) audio_state[6] = callback5;
    ((void (*)(void))(uintptr_t)config_callback)();
    gx8002_resident_request_irq_2553c(
        2u, (uint32_t)(uintptr_t)gx8002_resident_audio_irq_25e48, 0u);

    if (record_callback != 0u) {
        uint32_t selected = audio_state[1];
        if ((selected & 1u) != 0u) set_bit(0x100u, 0u);
        if ((selected & 2u) != 0u) set_bit(0x100u, 1u);
        if ((selected & 4u) != 0u) set_bit(0x100u, 2u);
    }
    uint32_t channels = audio_state[0];
    if ((channels & 1u) != 0u) {
        set_bit(0x0cu, 9u);
        clear_bit(0u, 7u);
    }
    if ((channels & 2u) != 0u) {
        if ((ain[0x28u / 4u] & 15u) < 2u) set_bit(0x28u, 9u);
        if ((ain[0x2cu / 4u] & 15u) < 2u) set_bit(0x2cu, 9u);
        clear_bit(0u, 15u);
    }
    if ((channels & 4u) != 0u) {
        if ((ain[0x48u / 4u] & 15u) < 8u) set_bit(0x48u, 9u);
        if ((ain[0x4cu / 4u] & 15u) < 8u) set_bit(0x4cu, 9u);
        clear_bit(4u, 31u);
    }
    return 0u;
}
