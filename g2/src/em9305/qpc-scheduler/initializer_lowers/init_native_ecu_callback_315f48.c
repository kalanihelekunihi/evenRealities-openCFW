#include <stdint.h>

/* Native 0x315f48..0x315f64: turn an ECU record pointer into its index in
 * the 912-byte record table at *0x805c70 and forward it with the byte at
 * 0x80281d. */
extern uint32_t opencfw_em9305_dispatch_child_323498(uint32_t,uint32_t);

uint32_t opencfw_em9305_ecu_callback_315f48(uintptr_t record)
{
    uint32_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
    int32_t index=(int32_t)((uint32_t)record-base)/912;
    uint32_t value=*(volatile uint8_t *)(uintptr_t)0x80281du;
    return opencfw_em9305_dispatch_child_323498((uint8_t)index,value);
}
