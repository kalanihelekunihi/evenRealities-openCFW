#include <stdint.h>
#include "native_battery_memory.h"
#include "native_stacmd.h"
extern uint32_t r1_yhm_register_read_record(uint32_t,uint32_t,uint8_t *);
uint32_t r1_yhm_register_read_native(uint32_t reg,uint32_t length,uint8_t *data)
{
    return r1_yhm_register_read_record(reg,(uint8_t)length,data);
}
uint32_t r1_yhm_register_read_byte_native(uint32_t reg,uint8_t *data)
{
    return r1_yhm_register_read_native(reg,1,data);
}
uint32_t r1_yhm_ready_native(void)
{
    volatile uint8_t *p=(volatile uint8_t *)&r1_stacmd;
    void (*select)(uint32_t,uint32_t)=(void *)(uintptr_t)read32(p+28);
    uint32_t line=p[32];
    select(read32(p+12),line);
    uint32_t (*probe)(uint32_t)=(void *)(uintptr_t)read32(p+40);
    return probe(read32(p+12))!=0;
}
