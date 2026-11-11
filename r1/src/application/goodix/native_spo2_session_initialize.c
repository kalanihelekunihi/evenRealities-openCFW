#include <stdint.h>
#include "goodix_mem.h"
#include "native_spo2_initialize.h"
static uint32_t word(uintptr_t p) { return *(const volatile uint32_t *)p; }
static void put32(uintptr_t p,uint32_t v) { *(volatile uint32_t *)p=v; }
static void put16(uintptr_t p,uint16_t v) { *(volatile uint16_t *)p=v; }
static void put8(uintptr_t p,uint8_t v) { *(volatile uint8_t *)p=v; }
/* Native descriptors from initialize_descriptor have nonzero divisors5/25.
 * Zero-divisor/trap behavior for malformed descriptors is outside this API. */
static uint32_t divided_capacity(uintptr_t p)
{
    return (uint32_t)(125/(int32_t)word(p));
}
uint32_t r1_goodix_native_extended_s16_queue_initialize(void *record,void *buffer,uint32_t count,uint32_t mode)
{
    if (!buffer) buffer=goodix_mem_malloc((int32_t)(count<<1));
    uintptr_t p=(uintptr_t)record;
    put16(p+4,0);put32(p,(uint32_t)(uintptr_t)buffer);put16(p+6,(uint16_t)count);
    put16(p+8,0);put8(p+11,(uint8_t)mode);put8(p+10,0);
    return 0;
}
uint32_t r1_goodix_spo2_short_pair_initialize(const void *descriptor,void *record)
{
    uintptr_t d=(uintptr_t)descriptor,p=(uintptr_t)record;
    put32(p,0);
    (void)r1_goodix_native_s16_queue_initialize((void *)(p+4),0,125);
    uint16_t count=(uint16_t)divided_capacity(d+92);
    return r1_goodix_native_s16_queue_initialize((void *)(p+16),0,count);
}
uint32_t r1_goodix_spo2_initialize_session_channel(const void *descriptor,void *record)
{
    uintptr_t d=(uintptr_t)descriptor,p=(uintptr_t)record;
    (void)r1_goodix_native_float_record_initialize((void *)p,0,25,1);
    (void)r1_goodix_native_float_record_initialize((void *)(p+16),0,word(d+80)+12u,1);
    (void)r1_goodix_native_float_record_initialize((void *)(p+32),0,25,1);
    (void)r1_goodix_native_float_record_initialize((void *)(p+48),0,1,1);
    (void)r1_goodix_native_float_record_initialize((void *)(p+64),0,divided_capacity(d+80),1);
    return r1_goodix_native_float_record_initialize((void *)(p+84),0,divided_capacity(d+84),1);
}
uint32_t r1_goodix_spo2_session_initialize(const void *descriptor,void *record)
{
    uintptr_t p=(uintptr_t)record;
    (void)r1_goodix_spo2_initialize_session_channel(descriptor,(void *)p);
    (void)r1_goodix_spo2_initialize_session_channel(descriptor,(void *)(p+100));
    (void)r1_goodix_native_float_record_initialize((void *)(p+200),0,125,1);
    (void)r1_goodix_native_float_record_initialize((void *)(p+216),0,125,1);
    (void)r1_goodix_native_float_record_initialize((void *)(p+232),0,125,1);
    return r1_goodix_native_extended_s16_queue_initialize((void *)(p+248),0,125,1);
}
