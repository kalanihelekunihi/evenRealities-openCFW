#include <stdint.h>
#include <stddef.h>
#include "goodix_mem.h"
#include "goodix_spo2.h"
#include "native_spo2_teardown.h"
#include "native_spo2_initialize.h"
extern void *memmove(void *,const void *,size_t);
extern void *memset(void *,int,size_t);
extern int strcmp(const char *,const char *);
/* Deeper constructors remain explicit boundaries, rather than guessed bodies. */
extern const void *r1_goodix_spo2_weights_get(void);
extern void *r1_goodix_spo2_model_create(const uint32_t *);
static uint32_t word(uintptr_t p) { return *(const volatile uint32_t *)p; }
static uint8_t byte(uintptr_t p) { return *(const volatile uint8_t *)p; }
static void put32(uintptr_t p,uint32_t v) { *(volatile uint32_t *)p=v; }
static void put16(uintptr_t p,uint16_t v) { *(volatile uint16_t *)p=v; }
static void put8(uintptr_t p,uint8_t v) { *(volatile uint8_t *)p=v; }
static uint32_t allocate(uint32_t size)
{ return (uint32_t)(uintptr_t)goodix_mem_malloc((int32_t)size); }
uint32_t r1_goodix_native_f32_queue_initialize(void *record,void *buffer,uint32_t count,uint32_t mode)
{
    (void)mode;
    if (!buffer) buffer=(void *)(uintptr_t)allocate(count<<2);
    uintptr_t p=(uintptr_t)record;
    put16(p+4,0);put32(p,(uint32_t)(uintptr_t)buffer);put16(p+6,(uint16_t)count);
    return 0;
}
uint32_t r1_goodix_native_s16_queue_initialize(void *record,void *buffer,uint32_t count)
{
    if (!buffer) buffer=(void *)(uintptr_t)allocate(count<<1);
    uintptr_t p=(uintptr_t)record;
    put16(p+4,0);put32(p,(uint32_t)(uintptr_t)buffer);put16(p+6,(uint16_t)count);
    return 0;
}
uint32_t r1_goodix_native_float_record_initialize(void *record,void *buffer,uint32_t count,uint32_t mode)
{
    uintptr_t p=(uintptr_t)record;
    uint32_t result=(uint32_t)p;
    if (buffer) put16(p+4,(uint16_t)count);
    else { result=allocate(count<<2);buffer=(void *)(uintptr_t)result;put16(p+4,0); }
    put8(p+9,0);put16(p+10,0);put32(p,(uint32_t)(uintptr_t)buffer);
    put16(p+6,(uint16_t)count);put8(p+8,(uint8_t)mode);put32(p+12,0);
    return result;
}
uint32_t r1_goodix_native_buffer_initialize(void *record)
{
    uintptr_t p=(uintptr_t)record;
    uint32_t allocation=allocate(64);
    put32(p,allocation);(void)memset((void *)(uintptr_t)allocation,0,64);
    put8(p+5,0);put8(p+4,0);put8(p+6,0);
    return 0;
}
uint32_t r1_goodix_spo2_initialize_descriptor(const void *configuration,void *descriptor)
{
    uintptr_t p=(uintptr_t)descriptor;
    (void)memmove(descriptor,configuration,76);
    put32(p+76,word(p+4)/25u);
    put32(p+80,5);put32(p+84,25);put32(p+88,1);put32(p+92,25);
    return 25;
}
uint32_t r1_goodix_spo2_allocate_pair(const void *descriptor,void *record)
{
    uintptr_t p=(uintptr_t)record;
    uint32_t allocation=allocate(word((uintptr_t)descriptor)*24u);
    put32(p+8,allocation);
    allocation=allocate(24);put32(p+24,allocation);
    return allocation;
}
uint32_t r1_goodix_spo2_initialize_descriptor_pair(const void *descriptor,void *record)
{
    (void)descriptor;
    (void)r1_goodix_native_f32_queue_initialize(record,0,20,1);
    return r1_goodix_native_f32_queue_initialize((void *)((uintptr_t)record+12),0,20,1);
}
uint32_t r1_goodix_spo2_initialize_aggregate(const void *descriptor,void *record)
{
    uintptr_t p=(uintptr_t)record;
    uint32_t allocation=allocate(260);put32(p,allocation);
    r1_goodix_spo2_session_initialize(descriptor,(void *)(uintptr_t)allocation);
    r1_goodix_spo2_short_pair_initialize(descriptor,(void *)(p+4));
    allocation=allocate(24);put32(p+28,allocation);
    return r1_goodix_spo2_initialize_descriptor_pair(descriptor,(void *)(uintptr_t)allocation);
}
uint32_t r1_goodix_spo2_initialize_owned(const void *descriptor,void *record)
{
    uintptr_t d=(uintptr_t)descriptor,p=(uintptr_t)record;
    put32(p,allocate(68));
    uintptr_t allocation=(uintptr_t)word(p);
    uint32_t second=byte(d+72),first=byte(d+71);
    return r1_goodix_native_float_record_initialize((void *)(allocation+4),0,
        second<first ? first : second,1);
}
uint32_t r1_goodix_spo2_initialize_buffer_owner(void *record,const void *descriptor)
{
    (void)descriptor;
    uintptr_t p=(uintptr_t)record;
    put32(p,allocate(8));
    return r1_goodix_native_buffer_initialize((void *)(uintptr_t)word(p));
}
uint32_t r1_goodix_spo2_initialize_model_owner(void *record)
{
    uintptr_t p=(uintptr_t)record;
    put8(p+8,1);put8(p+9,1);put8(p+10,125);put8(p+11,1);put8(p+12,1);put8(p+13,125);
    put32(p+16,1);put32(p+20,2);put32(p+24,1);
    volatile uint32_t parameters[4]={4,0,0,0};
    parameters[1]=(uint32_t)(uintptr_t)r1_goodix_spo2_weights_get();
    put32(p+28,(uint32_t)(uintptr_t)r1_goodix_spo2_model_create((const uint32_t *)(uintptr_t)parameters));
    /* Native POP restores R0 from the overwritten template slot. */
    return parameters[0];
}
uint32_t r1_goodix_spo2_initialize_channels(const void *descriptor,void *record)
{
    uintptr_t d=(uintptr_t)descriptor,p=(uintptr_t)record;
    if (!word(d+28)) return 0;
    put32(p,allocate(word(d)*40u));
    for (uint32_t i=0;;++i) {
        uint32_t count=word(d);
        if (count<=i) return count;
        uintptr_t item=(uintptr_t)word(p)+i*40u;
        put8(item+36,byte(d+32));put8(item+8,0);put32(item+12,0);put32(item+16,0);
        (void)r1_goodix_native_float_record_initialize((void *)(item+20),0,15,1);
    }
}
goodix_spo2_ret goodix_spo2_init(const void *configuration,int32_t size,char *interface)
{
    r1_goodix_native_spo2_context=0;
    if (!configuration || size!=76 || strcmp(interface,"pre_pv_v1.1.0")) return 6;
    void *allocation=goodix_mem_malloc(212);
    r1_goodix_native_spo2_context=allocation;
    (void)memset(allocation,0,212);
    uintptr_t p=(uintptr_t)r1_goodix_native_spo2_context;
    (void)r1_goodix_spo2_initialize_descriptor(configuration,(void *)(p+12));
    p=(uintptr_t)r1_goodix_native_spo2_context;
    (void)r1_goodix_spo2_allocate_pair((void *)(p+12),(void *)(p+108));
    p=(uintptr_t)r1_goodix_native_spo2_context;
    (void)r1_goodix_spo2_initialize_aggregate((void *)(p+12),(void *)(p+136));
    p=(uintptr_t)r1_goodix_native_spo2_context;
    (void)r1_goodix_spo2_initialize_owned((void *)(p+12),(void *)(p+168));
    p=(uintptr_t)r1_goodix_native_spo2_context;
    (void)r1_goodix_spo2_initialize_buffer_owner((void *)(p+172),(void *)(p+12));
    p=(uintptr_t)r1_goodix_native_spo2_context;
    (void)r1_goodix_spo2_initialize_model_owner((void *)(p+176));
    p=(uintptr_t)r1_goodix_native_spo2_context;
    (void)r1_goodix_spo2_initialize_channels((void *)(p+12),(void *)(p+208));
    return GX_ALGO_SPO2_SUCCESS;
}
