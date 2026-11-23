#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x315f48..0x315f64: turn an ECU record pointer into its index in
 * the 912-byte record table at *((uintptr_t)&em9305_ram_805c5c + 0x14u) and forward it with the byte at
 * ((uintptr_t)&em9305_ram_8027e0 + 0x3du). */
extern uint32_t opencfw_em9305_dispatch_child_323498(uint32_t,uint32_t);

uint32_t opencfw_em9305_ecu_callback_315f48(uintptr_t record)
{
    uint32_t base=em9305_ram_805c5c.u32_805c70;
    int32_t index=(int32_t)((uint32_t)record-base)/912;
    uint32_t value=em9305_ram_8027e0.u8_80281d;
    return opencfw_em9305_dispatch_child_323498((uint8_t)index,value);
}
