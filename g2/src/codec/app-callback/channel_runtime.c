/* Decoded XIP channel callback/stop and timer-ready bodies.
 * Stock envelopes 0x10203630..0x10203686 and 0x102077a8..0x102077ce.
 * Resident critical save/restore are genuine unresolved ABI contracts.
 */
#include <stdint.h>
extern uint32_t g2_codec_critical_save(void); /* 0x10025560 */
extern void g2_codec_critical_restore(uint32_t state); /* 0x1002556c */
static volatile uint32_t *channel_address(uint32_t channel)
{
    return (volatile uint32_t *)(uintptr_t)(UINT32_C(0x20026a94) + (channel << 7));
}
uint32_t g2_codec_channel_callback_set(uint32_t index, uintptr_t callback, uint32_t argument)
{
    volatile uint32_t *const channel = channel_address(index);
    if (callback == 0) return UINT32_MAX;
    channel[17] = 1;
    channel[18] = (uint32_t)callback;
    channel[19] = argument;
    const uint32_t state = g2_codec_critical_save();
    volatile uint32_t *const registers = (volatile uint32_t *)(uintptr_t)channel[1];
    const uint32_t old = registers[1];
    registers[1] = old | 2u;
    g2_codec_critical_restore(state);
    return 0;
}
uint32_t g2_codec_channel_stop(uint32_t index)
{
    volatile uint32_t *const channel = channel_address(index);
    channel[18] = 0;
    channel[19] = 0;
    const uint32_t state = g2_codec_critical_save();
    volatile uint32_t *const registers = (volatile uint32_t *)(uintptr_t)channel[1];
    const uint32_t old = registers[1];
    registers[1] = old & ~UINT32_C(2);
    g2_codec_critical_restore(state);
    return 0;
}
/* Stock 0x102077A8 (gx8002_power_lock) */
uint32_t g2_codec_channel_timer_start(uint32_t timer)
{
    const uint32_t count = timer - 1u;
    uint32_t bit = 1;
    /* Keep decoded hardware shift behavior for every input, including >31. */
    __asm__ volatile("lsl %0, %1" : "+r"(bit) : "r"(count) : "cc");
    volatile uint32_t *const timer_state = (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002dfbc);
    const uint32_t allowed = timer_state[1];
    if ((allowed & bit) == 0) return UINT32_MAX;
    if ((int32_t)timer >= 33) return UINT32_MAX;
    const uint32_t pending = timer_state[0];
    timer_state[0] = bit | pending;
    return 0;
}
