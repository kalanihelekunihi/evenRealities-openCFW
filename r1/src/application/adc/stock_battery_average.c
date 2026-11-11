/* Native 50c90 averaging policy; native sample frame lives in its bridge. */
#include <stdint.h>
#include "../registry/stock_registry.h"
#include "../i2c5/stock_transport.h"
extern void r1_rtt_delay_cycles(uint32_t);
__attribute__((used,noinline)) uint32_t r1_adc_channel_read_averaged_body(
    volatile int16_t *sample)
{
    *sample = 0;
    (void)r1_stock_dispatch_08(r1_vnfc_rect_adc_device);
    for (uint32_t wait = 0; wait < 10; ++wait)
        r1_rtt_delay_cycles(64000);
    int32_t total = 0;
    for (uint32_t index = 0; index < 3; ++index) {
        (void)r1_stock_dispatch_10(r1_vnfc_rect_adc_device, 0,
                                  (uintptr_t)sample, 1);
        if (*sample < 0)
            *sample = 0;
        total += *sample;
        *sample = 0;
    }
    (void)r1_stock_dispatch_0c(r1_vnfc_rect_adc_device);
    return (uint16_t)(total / 3);
}
extern uint32_t r1_adc_channel_read_averaged(void);
/* Native name is historical; preserve the integer scaling, without clamping
 * or claiming this returned word is a percentage in 0..100. */
uint16_t r1_battery_raw_to_percent(void)
{
    uint32_t raw = r1_adc_channel_read_averaged();
    uint32_t scaled = ((raw * 3600u + 2048u) >> 12) & 0xffffu;
    return (uint16_t)((scaled * 331u) / 51u);
}

/* Historical name at 50d2a: raw ADC average followed by an independently
 * acquired/scaled ADC value. Keep the first store before the second read. */
void r1_temperature_pair_read(volatile uint16_t *out)
{
    out[0] = (uint16_t)r1_adc_channel_read_averaged();
    out[1] = r1_battery_raw_to_percent();
}
