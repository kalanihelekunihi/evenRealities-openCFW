#include <stdint.h>

/* Stock 0x00590b92..0x00590c61. A valid handle points to at least
 * 0x64 bytes; the native function reads handle+4 before checking NULL. */
extern uint32_t audio_power_clock_acquire(uint32_t clock, uint32_t user);
extern uint32_t audio_power_clock_release(uint32_t clock, uint32_t user);
extern uint32_t audio_i2s_clock_source(uint32_t source);
extern void audio_power_reconfigure(uint32_t instance, uint32_t source);

enum { I2S_BASE = 0x40208000u, I2S_MARKER = 0x01125125u };

uint32_t g2_codec_i2s_prepare(void *handle) {
    uint32_t *const words = (uint32_t *)handle;
    uint32_t const instance = words[1];
    uint32_t const user = instance == 0u ? 29u : 30u;
    if (handle == 0 || (words[0] & 0x01ffffffu) != I2S_MARKER)
        return 2u;
    if ((words[0] & 0x02000000u) != 0u)
        return 0u;

    uint32_t status = audio_power_clock_acquire(4u, user);
    if (status != 0u)
        return status;

    volatile uint32_t *const control = (volatile uint32_t *)(uintptr_t)
        (I2S_BASE + (instance << 12) + 0x100u);
    if (((const uint8_t *)handle)[0x60] == 0u) {
        audio_power_reconfigure(instance, 0x217u);
        *control &= ~1u;
        *control &= ~0x1000u;
    } else {
        uint32_t const source = words[0x5cu / 4u];
        uint32_t const clock = (uint8_t)audio_i2s_clock_source(source);
        status = audio_power_clock_acquire(clock, user);
        if (status != 0u) {
            (void)audio_power_clock_release(4u, user);
            return status;
        }
        audio_power_reconfigure(instance, source);
        *control |= 1u;
        *control |= 0x1000u;
    }
    words[0] |= 0x02000000u;
    return 0u;
}
