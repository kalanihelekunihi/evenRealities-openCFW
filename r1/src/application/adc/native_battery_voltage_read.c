/* Stock 0x506a4 acquires three signed samples from the YHM
 * vpmic_isns_adc handle. Reload the handle at every dispatch boundary. */
#include <stdint.h>
#include "../registry/stock_registry.h"
#include "../board/native_battery_memory.h"
extern volatile uint8_t r1_yhm_transport_context[];
uint32_t r1_battery_voltage_read(void)
{
    volatile uint32_t storage=0;
    volatile int16_t *sample=(volatile int16_t *)&storage;
    volatile uint8_t *context=r1_yhm_transport_context;
    int32_t total=0;
    (void)r1_stock_dispatch_08((void *)(uintptr_t)read32(context+16));
    for (uint32_t index=0;index<3;++index) {
        (void)r1_stock_dispatch_10((void *)(uintptr_t)read32(context+16),
                                 0,(uintptr_t)sample,1);
        if (*sample<0) *sample=0;
        total+=*sample;
        *sample=0;
    }
    (void)r1_stock_dispatch_0c((void *)(uintptr_t)read32(context+16));
    uint32_t average=(uint16_t)(total/3);
    return (average*1200u+2048u)>>12;
}
