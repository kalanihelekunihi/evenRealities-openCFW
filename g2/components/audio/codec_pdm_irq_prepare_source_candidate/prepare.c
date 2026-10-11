#include <stdint.h>

/* Stock 0x00592230..0x005922d5. The clock and timing children retain
 * their actual source contracts; this body preserves the reset pulse,
 * acquisition rollback and control-register order. */
extern uint32_t g2_pdm_clock_source(int32_t source); /* 0x591d14 */
extern uint32_t audio_power_clock_acquire(uint32_t clock, uint32_t user);
extern uint32_t audio_power_clock_release(uint32_t clock, uint32_t user);
extern void g2_pdm_clock_select(uint32_t instance, int32_t source); /* 0x591d7a */
extern void stock_delay_us(uint32_t us);

uint32_t g2_pdm_irq_prepare(void *handle) {
    const uint32_t *const row = (const uint32_t *)handle;
    if (handle == 0 || (row[0] & 0x01ffffffu) != 0x01f956e2u)
        return 2u;
    uint32_t const instance = row[2];
    int32_t const source = *(const int16_t *)((const uint8_t *)handle + 28u);
    uint32_t const clock = (uint8_t)g2_pdm_clock_source(source);
    volatile uint32_t *const control = (volatile uint32_t *)(uintptr_t)
        (0x40201000u + (instance << 12));
    *control &= ~0x10u;
    stock_delay_us(100u);
    *control |= 0x10u;
    uint32_t status = audio_power_clock_acquire(4u, 28u);
    if (status != 0u)
        return status;
    status = audio_power_clock_acquire(clock, 28u);
    if (status != 0u) {
        (void)audio_power_clock_release(4u, 28u);
        return status;
    }
    g2_pdm_clock_select(instance, source);
    *control |= 1u;
    *control |= 0x40u;
    return 0u;
}
