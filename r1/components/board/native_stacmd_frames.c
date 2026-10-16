#include "native_stacmd.h"
#include <stdint.h>
#include "native_battery_memory.h"
static void release_line(uint32_t reading)
{
    volatile uint8_t *p=(volatile uint8_t *)&r1_stacmd;
    uint32_t pin,line;
    if (reading) { line=p[32];pin=read32(p+12); }
    else { pin=read32(p+12);line=p[32]; }
    void (*release)(uint32_t,uint32_t)=(void *)(uintptr_t)read32(p+28);
    release(pin,line);
}
uint32_t r1_stacmd_read_frame_native(uint32_t command,uint32_t reg,uint32_t length,uint8_t *bytes)
{
    if (!(command&0x40)) goto fail;
    r1_stacmd_idle_native();
    uint32_t header=(uint8_t)((command&0xf0)+reg),received;
    r1_stacmd_write_bits_native(header,1);
    r1_stacmd_drive_bit_native(1);
    if (!r1_stacmd_read_bit_adapter_native(&received)) goto fail;
    if (r1_stacmd_parity_native((uint8_t)(1+(header<<1)))!=received) goto fail;
    for (uint32_t index=0;(int32_t)index<(int32_t)length;index++) {
        uint8_t value=0;
        for (int32_t bit=7;bit>=0;bit--) {
            if (!r1_stacmd_read_bit_native(&received)) { bytes[index]=value;goto fail; }
            value=(uint8_t)(value+(received<<bit));
        }
        bytes[index]=value;
        if (index!=length-1)
            r1_stacmd_drive_bit_native(r1_stacmd_parity_native(bytes[index])==1 ? 1 : 0);
    }
    r1_stacmd_idle_native();release_line(1);return 1;
fail:
    r1_stacmd_idle_native();return 0;
}
uint32_t r1_stacmd_write_frame_native(uint32_t command,uint32_t reg,uint32_t length,const uint8_t *bytes)
{
    if (!(command&0x40)) goto fail;
    uint32_t header=(uint8_t)((command&0xf0)+reg),received;
    r1_stacmd_idle_native();r1_stacmd_write_bits_native(header,1);r1_stacmd_drive_bit_native(0);
    if (!r1_stacmd_read_bit_adapter_native(&received)) goto fail;
    if (r1_stacmd_parity_native((uint8_t)(header<<1))!=received) goto fail;
    for (uint32_t index=0;(int32_t)index<(int32_t)length;index++) {
        r1_stacmd_write_bits_native(bytes[index],0);
        if (!r1_stacmd_read_bit_adapter_native(&received)) goto fail;
        if (r1_stacmd_parity_native(bytes[index])!=received) goto fail;
    }
    r1_stacmd_idle_native();release_line(0);return 1;
fail:
    r1_stacmd_idle_native();return 0;
}
