#include <stdint.h>
#include "native_battery_memory.h"
#include "../registry/stock_registry.h"
extern volatile uint8_t r1_yhm_transport_context[];
static generic_device_registry_device *handle(uint32_t offset)
{ return (void *)(uintptr_t)read32(r1_yhm_transport_context+offset); }
void r1_yhm_device_handles_initialize(void)
{
    if (!handle(4)) write32(r1_yhm_transport_context+4,(uintptr_t)r1_stock_registry_find("device_stacmd"));
    if (!handle(8)) {
        generic_device_registry_device *ship=r1_stock_registry_find("ship_mode_en");
        write32(r1_yhm_transport_context+8,(uintptr_t)ship);
        (void)r1_stock_dispatch_08(ship);
        (void)r1_stock_dispatch_18(handle(8),0,0);
    }
    if (!handle(12)) write32(r1_yhm_transport_context+12,(uintptr_t)r1_stock_registry_find("device_stacmd_irq"));
    if (!handle(16)) write32(r1_yhm_transport_context+16,(uintptr_t)r1_stock_registry_find("vpmic_isns_adc"));
}

extern void r1_rtt_delay_cycles(uint32_t);
/* Preserve the handle reload and calibrated delay calls using ordinary C.
 * The architectural delay primitive remains a separate implementation. */
__attribute__((noinline)) void r1_analog_init_delay(void)
{
    (void)r1_stock_dispatch_08(handle(8));
    (void)r1_stock_dispatch_18(handle(8),1,0);
    for (uint32_t i=0;i<200;++i) r1_rtt_delay_cycles(64000);
}
void r1_sysctl_op_sequence_thunk(void)
{
    r1_analog_init_delay();
}
