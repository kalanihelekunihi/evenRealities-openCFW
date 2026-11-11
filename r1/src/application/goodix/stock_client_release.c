/* Stock 50be0; state cells 200076c4/c8 and counters 2001e51c..e543.
 * Acquisition/startup ownership is not inferred from this release policy. */
#include <stdint.h>
volatile uint32_t r1_goodix_active_mask
    __attribute__((section(".bss.r1.goodix.active.mask"), aligned(4)));
volatile uintptr_t r1_goodix_release_callback
    __attribute__((section(".bss.r1.goodix.release.callback"), aligned(4)));
volatile uint32_t r1_goodix_client_counts[10]
    __attribute__((section(".bss.r1.goodix.client.counts"), aligned(4)));
static const uint32_t r1_goodix_mode_masks[9] =
    {0, 2, 0x40, 0x200, 4, 8, 0, 1, 0x2000};
extern void r1_goodix_i2c_open(void);
extern void r1_goodix_i2c_close(void);
extern uint32_t r1_goodix_irq_close(void);
extern void r1_goodix_power_disable(void);
extern void r1_goodix_transport_release(void);
extern void r1_shared_power_client_release(uint32_t);
extern void Gh3x2xDemoStopSampling(uint32_t);
uint32_t r1_goodix_reference_counted_release(uint32_t selector)
{
    uint32_t index;
    switch (selector) {
    case 1: index = 1; break;
    case 2: case 6: index = 2; break;
    case 3: index = 3; break;
    case 4: index = 4; break;
    case 5: index = 5; break;
    case 7: index = 7; break;
    case 8: case 9:
        r1_goodix_i2c_open();
        Gh3x2xDemoStopSampling(r1_goodix_mode_masks[8]);
        (void)r1_goodix_irq_close();
        r1_goodix_power_disable();
        r1_goodix_i2c_close();
        r1_goodix_transport_release();
        r1_shared_power_client_release(1);
        return 1;
    default: return 0;
    }
    uint32_t count = r1_goodix_client_counts[index];
    if (count == 0)
        return 1;
    --count;
    r1_goodix_client_counts[index] = count;
    if (count != 0)
        return 1;
    uint32_t mask = r1_goodix_mode_masks[index];
    r1_goodix_active_mask = r1_goodix_active_mask & ~mask;
    r1_goodix_i2c_open();
    Gh3x2xDemoStopSampling(mask);
    r1_goodix_i2c_close();
    if (r1_goodix_active_mask == 0) {
        (void)r1_goodix_irq_close();
        r1_goodix_power_disable();
        r1_goodix_i2c_close();
        r1_goodix_transport_release();
        r1_shared_power_client_release(1);
        uintptr_t callback = r1_goodix_release_callback;
        if (callback != 0)
            ((void (*)(uint32_t))callback)(1);
    }
    return 1;
}

/* Matching native 50b00 acquire policy uses the same state and mode table. */
extern void r1_shared_power_client_acquire(uint32_t);
extern void r1_goodix_power_enable(void);
extern void r1_goodix_transport_prepare(void);
extern uint32_t r1_goodix_irq_prepare(void);
extern void nrf_delay_ms(uint32_t);
extern int Gh3x2xDemoInit(void);
extern int8_t Gh3x2xDemoArrayCfgSwitch(uint8_t);
extern void Gh3x2xDemoStartSampling(uint32_t);
extern int8_t GH3X2X_FifoWatermarkThrConfig(uint16_t);
uint32_t r1_goodix_reference_counted_acquire(uint32_t selector)
{
    uint32_t index;
    switch (selector) {
    case 1: index = 1; break;
    case 2: case 6: index = 2; break;
    case 3: index = 3; break;
    case 4: index = 4; break;
    case 5: index = 5; break;
    case 7: index = 7; break;
    case 8: case 9: index = 8; break;
    default: return 0;
    }
    uint32_t mode = r1_goodix_mode_masks[index];
    if (index == 8) {
        r1_shared_power_client_acquire(1);
        r1_goodix_power_enable();
        r1_goodix_transport_prepare();
        r1_goodix_i2c_open();
        nrf_delay_ms(10);
        (void)Gh3x2xDemoInit();
        (void)r1_goodix_irq_prepare();
        (void)Gh3x2xDemoArrayCfgSwitch(2);
        Gh3x2xDemoStartSampling(mode);
        (void)GH3X2X_FifoWatermarkThrConfig(5);
    } else {
        uint32_t count = r1_goodix_client_counts[index] + 1;
        r1_goodix_client_counts[index] = count;
        if (count > 1)
            return 1;
        uint32_t cold = r1_goodix_active_mask == 0;
        if (cold) {
            r1_shared_power_client_acquire(1);
            r1_goodix_transport_prepare();
            r1_goodix_power_enable();
            (void)r1_goodix_irq_prepare();
            r1_goodix_i2c_open();
            (void)Gh3x2xDemoArrayCfgSwitch(0);
            r1_goodix_i2c_close();
        }
        r1_goodix_active_mask = r1_goodix_active_mask | mode;
        r1_goodix_i2c_open();
        Gh3x2xDemoStartSampling(mode);
        if (cold) {
            (void)GH3X2X_FifoWatermarkThrConfig(25);
            uintptr_t callback = r1_goodix_release_callback;
            if (callback != 0)
                ((void (*)(uint32_t))callback)(0);
        }
    }
    r1_goodix_i2c_close();
    return 1;
}

/* Native 50904 uses CMSIS osDelay ticks, not the Nordic busy delay. */
extern int32_t osDelay(uint32_t);
void r1_goodix_switch_profile(uint32_t selector)
{
    r1_goodix_power_enable();
    r1_goodix_transport_prepare();
    r1_goodix_i2c_open();
    (void)osDelay(100);
    (void)Gh3x2xDemoArrayCfgSwitch(0);
    Gh3x2xDemoStopSampling(0x42);
    (void)osDelay(10);
    if (selector > 1)
        return;
    __attribute__((musttail)) return Gh3x2xDemoStartSampling(selector == 0 ? 2 : 0x40);
}

/* Native 509e0 proves the complete ten-word initialization span. */
extern void __aeabi_memclr(void *, uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t, const char *, const char *, ...);
extern void nrf_log_frontend_std_1(uint32_t, const char *, uint32_t);
uint32_t r1_goodix_initialize_probe(void)
{
    static const char format[] = "[RING]%s ppg init\r\n";
    r1_goodix_active_mask = 0;
    __aeabi_memclr((void *)r1_goodix_client_counts, 40);
    r1_goodix_power_enable();
    r1_goodix_transport_prepare();
    r1_goodix_i2c_open();
    nrf_delay_ms(10);
    int result = Gh3x2xDemoInit();
    const char *status = result == 0 ? "success" : "failed";
    if ((r1_structured_log_mode_get() & 1u) ||
        (r1_structured_log_mode_get() & 4u))
        (void)r1_structured_log_format(0x0c400000, format, format, status);
    if (r1_structured_log_mode_get() & 2u)
        nrf_log_frontend_std_1(0x001c0003, "%s ppg init\r\n", (uint32_t)(uintptr_t)status);
    r1_goodix_i2c_close();
    r1_goodix_transport_release();
    (void)r1_goodix_irq_close();
    r1_goodix_power_disable();
    return result == 0;
}

/* Direct native lifecycle entries 50870/50892/508b6. */
extern void Gh3x2xDemoStartSamplingWithCfgSwitch(uint32_t, uint8_t);
void r1_goodix_stop_stock_profiles(void)
{
    Gh3x2xDemoStopSampling(0x2000);
    Gh3x2xDemoStopSampling(0x4000);
    r1_goodix_i2c_close();
    r1_goodix_transport_release();
    __attribute__((musttail)) return r1_goodix_power_disable();
}
void r1_goodix_start_profile_4000(void)
{
    r1_goodix_power_enable();
    r1_goodix_transport_prepare();
    r1_goodix_i2c_open();
    (void)osDelay(10);
    (void)Gh3x2xDemoInit();
    return Gh3x2xDemoStartSamplingWithCfgSwitch(0x4000, 2);
}
void r1_goodix_start_profile_2000(void)
{
    r1_goodix_power_enable();
    r1_goodix_transport_prepare();
    r1_goodix_i2c_open();
    (void)osDelay(10);
    (void)Gh3x2xDemoInit();
    return Gh3x2xDemoStartSamplingWithCfgSwitch(0x2000, 2);
}
/* Native 2e734 tests the communication result and returns full-width -91
 * for zero, zero otherwise. Do not invert this to a presumed success test. */
extern int8_t GH3X2X_CommunicateConfirm(void);
int32_t r1_goodix_sampling_mode_glue(void)
{
    return GH3X2X_CommunicateConfirm() == 0 ? -91 : 0;
}
uint8_t r1_goodix_identity_probe(void)
{
    r1_goodix_power_enable();
    r1_goodix_transport_prepare();
    nrf_delay_ms(50);
    r1_goodix_i2c_open();
    uint8_t result = (uint8_t)r1_goodix_sampling_mode_glue();
    r1_goodix_i2c_close();
    r1_goodix_transport_release();
    r1_goodix_power_disable();
    return result;
}

/* Native 50998: install/clear the shared power callback word verbatim.
 * Native R0 is unchanged on return; retain that observable word as well. */
uint32_t r1_health_module_field_set(uint32_t callback)
{
    r1_goodix_release_callback = callback;
    return callback;
}
