/* Stock 0x50c90 exposes a signed halfword sample to the synchronous ADC
 * dispatcher. Its saved-register frame is private implementation storage. */
#include <stdint.h>
extern uint32_t r1_adc_channel_read_averaged_body(volatile int16_t *sample);
uint32_t r1_adc_channel_read_averaged(void)
{
    volatile uint32_t storage=0;
    return r1_adc_channel_read_averaged_body((volatile int16_t *)&storage);
}
