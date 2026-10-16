#include "native_stacmd.h"
#include <stdint.h>
#include "native_battery_memory.h"
static uint32_t sample_pin(void)
{
    volatile uint8_t *p=(volatile uint8_t *)&r1_stacmd;
    uint32_t (*read_pin)(uint32_t)=(void *)(uintptr_t)read32(p+40);
    return read_pin(read32(p+12));
}
uint32_t r1_stacmd_read_bit_native(uint32_t *bit)
{
    volatile uint8_t *p=(volatile uint8_t *)&r1_stacmd;
    void (*input)(uint32_t,uint32_t)=(void *)(uintptr_t)read32(p+28);
    uint32_t pull=p[32];
    input(read32(p+12),pull);
    uint32_t valid=1,count;
    for (count=0;count<1000;count++) if (sample_pin()!=1) break;
    if (count==1000) valid=0;
    for (uint32_t i=0;i<26;i++) __asm__ volatile("nop\nnop\nnop\nnop");
    uint32_t sample=sample_pin();
    for (count=0;count<1000;count++) if (sample_pin()!=0) break;
    if (count==1000) valid=0;
    *bit=(~sample)&1u;
    return valid;
}
uint32_t r1_stacmd_read_bit_adapter_native(uint32_t *bit)
{
    uint32_t received;
    uint32_t result=r1_stacmd_read_bit_native(&received);
    *bit=received;
    return result;
}
