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
/* Stock 0x28bb0 read policy. ACK/data words are explicit local outputs;
 * private frames and incidental caller-clobbered register returns are not
 * part of the typed frame API. Bit timing remains in the existing drivers. */
__attribute__((noinline)) uint32_t r1_stacmd_read_frame_native(
 uint32_t command,uint32_t reg,uint32_t length,uint8_t *bytes)
{
    volatile struct {uint32_t ack,data,header;} frame;
    _Static_assert(sizeof(frame)==12,"STACMD read C local extent");
    frame.ack=length;frame.data=(uint32_t)(uintptr_t)bytes;
    uint32_t result=0;
    volatile uint8_t *output=bytes;
    if (!(command&0x40u)) goto fail;
    r1_stacmd_idle_native();
    frame.header=(uint8_t)((command&0xf0u)+reg);
    r1_stacmd_write_bits_native(frame.header,1);
    r1_stacmd_drive_bit_native(1);
    if (!r1_stacmd_read_bit_adapter_native((uint32_t *)(uintptr_t)&frame.ack)) goto fail;
    uint32_t expected=r1_stacmd_parity_native((uint8_t)(1+(frame.header<<1)));
    if (expected!=frame.ack) goto fail;
    for (uint32_t index=0;(int32_t)index<(int32_t)length;index++) {
        uint8_t value=0;
        for (int32_t bit=7;bit>=0;bit--) {
            if (!r1_stacmd_read_bit_native((uint32_t *)(uintptr_t)&frame.data)) {
                output[index]=value;goto fail;
            }
            value=(uint8_t)(value+(frame.data<<bit));
        }
        output[index]=value;
        if (index!=length-1) {
            uint32_t byte=output[index];
            expected=r1_stacmd_parity_native(byte);
            r1_stacmd_drive_bit_native(expected==1 ? 1 : 0);
        }
    }
    r1_stacmd_idle_native();release_line(1);result=1;goto done;
fail:
    r1_stacmd_idle_native();
done:;
    return result;
}
/* Stock 0x28c6c write policy, with explicit ACK storage. */
__attribute__((noinline)) uint32_t r1_stacmd_write_frame_native(
 uint32_t command,uint32_t reg,uint32_t length,const uint8_t *bytes)
{
    volatile struct {uint32_t word,header;} frame;
    _Static_assert(sizeof(frame)==8,"STACMD write C local extent");
    frame.word=(uint32_t)(uintptr_t)bytes;
    uint32_t result=0;
    const volatile uint8_t *data=bytes;
    if (!(command&0x40u)) goto fail;
    frame.header=(uint8_t)((command&0xf0u)+reg);
    r1_stacmd_idle_native();r1_stacmd_write_bits_native(frame.header,1);r1_stacmd_drive_bit_native(0);
    if (!r1_stacmd_read_bit_adapter_native((uint32_t *)(uintptr_t)&frame.word)) goto fail;
    uint32_t expected=r1_stacmd_parity_native((uint8_t)(frame.header<<1));
    if (expected!=frame.word) goto fail;
    for (uint32_t index=0;(int32_t)index<(int32_t)length;index++) {
        uint32_t byte=data[index];
        r1_stacmd_write_bits_native(byte,0);
        if (!r1_stacmd_read_bit_adapter_native((uint32_t *)(uintptr_t)&frame.word)) goto fail;
        byte=data[index];
        expected=r1_stacmd_parity_native(byte);
        if (expected!=frame.word) goto fail;
    }
    r1_stacmd_idle_native();release_line(0);result=1;goto done;
fail:
    r1_stacmd_idle_native();
done:;
    return result;
}
