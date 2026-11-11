#include <stdint.h>
#include <stddef.h>
#include "goodix_mem.h"
#include "goodix_hrv.h"
#include "native_hrv_calc.h"
extern int strcmp(const char *,const char *);
extern void *memset(void *,int,size_t);
extern void *volatile r1_goodix_native_hrv_context;
static uint32_t word(uintptr_t p) { return *(const volatile uint32_t *)p; }
static void put(uintptr_t p,uint32_t value) { *(volatile uint32_t *)p=value; }
static uintptr_t context(void) { return (uintptr_t)r1_goodix_native_hrv_context; }
uint32_t r1_goodix_native_float_storage_initialize(void *record,void *buffer,uint32_t capacity)
{
    uintptr_t p=(uintptr_t)record;
    if (buffer) { put(p+4,capacity);put(p+12,capacity); }
    else {
        uint32_t bytes=capacity<<2;
        buffer=goodix_mem_malloc((int32_t)bytes);
        if (!buffer) return 1;
        (void)memset(buffer,0,bytes);put(p+4,0);put(p+12,0);
    }
    put(p,(uint32_t)(uintptr_t)buffer);put(p+8,capacity);
    return 0;
}
static uint32_t storage(uint32_t offset,uint32_t capacity)
{ return r1_goodix_native_float_storage_initialize((void *)(context()+offset),NULL,capacity); }
goodix_hrv_ret goodix_hrv_init(const void *configuration,uint32_t size,const char *interface)
{
    uintptr_t cfg=(uintptr_t)configuration;
    if (!configuration || size!=24 || strcmp(interface,"pv_v1.1.0")) return GX_HRV_ALGO_FAILED;
    if (r1_goodix_native_hrv_context) return GX_HRV_ALGO_NULL_PTR;
    r1_goodix_hrv_calculation_unbind();
    void *allocation=goodix_mem_malloc(308);
    r1_goodix_native_hrv_context=allocation;
    if (!allocation) return GX_HRV_ALGO_OUT_OF_MEM;
    (void)memset(allocation,0,308);
    uintptr_t p=context();put(p,word(cfg));
    uint32_t rate=word(cfg+4);put(p+8,rate);
    uint32_t mode,count,first,second=65,initial=1;
    if (rate>=25 && rate<=975 && rate%50==25) { mode=0;count=rate/25;first=37; }
    else if (rate>=50 && rate<=950 && rate%100==50) { mode=1;count=rate/50;first=75; }
    else if (rate>=100 && rate<=900 && rate%200==100) { mode=2;count=rate/100;first=151; }
    else if (rate>=200 && rate<=1000 && rate%200==0) { mode=3;count=rate/200;first=251;second=129; }
    else { mode=0;count=1;first=151;initial=(uint32_t)((int32_t)rate/25); }
    put(p+0x124,first);put(p+0x14,mode);put(p+0x18,count);put(p+0x128,second);put(p+0x12c,initial);
    if (r1_goodix_native_float_storage_initialize((void *)(p+0x1c),NULL,word(p+0x12c))==1) return GX_HRV_ALGO_OUT_OF_MEM;
    if (storage(0x94,11)==1) return GX_HRV_ALGO_OUT_OF_MEM;
    if (storage(0xa8,10)==1) return GX_HRV_ALGO_OUT_OF_MEM;
    if (storage(0xb8,10)==1) return GX_HRV_ALGO_OUT_OF_MEM;
    if (storage(0xc8,10)==1) return GX_HRV_ALGO_OUT_OF_MEM;
    p=context();if (r1_goodix_native_float_storage_initialize((void *)(p+0x2c),NULL,word(p+0x18))==1) return GX_HRV_ALGO_OUT_OF_MEM;
    p=context();if (r1_goodix_native_float_storage_initialize((void *)(p+0x3c),NULL,word(p+0x124))==1) return GX_HRV_ALGO_OUT_OF_MEM;
    p=context();if (r1_goodix_native_float_storage_initialize((void *)(p+0x4c),NULL,word(p+0x128))==1) return GX_HRV_ALGO_OUT_OF_MEM;
    if (storage(0x5c,4)==1) return GX_HRV_ALGO_OUT_OF_MEM;
    if (storage(0x74,125)==1) return GX_HRV_ALGO_OUT_OF_MEM;
    p=context();int32_t signed_rate=(int32_t)word(p+8);
    uint32_t capacity=signed_rate%25 ? 5 : (uint32_t)(signed_rate/25);
    if (r1_goodix_native_float_storage_initialize((void *)(p+0x84),NULL,capacity)==1) return GX_HRV_ALGO_OUT_OF_MEM;
    p=context();put(p+4,0);put(p+0x130,0);
    allocation=goodix_mem_malloc(48);put(context()+0x6c,(uint32_t)(uintptr_t)allocation);
    if (!allocation) return GX_HRV_ALGO_OUT_OF_MEM;
    (void)memset(allocation,0,48);put(word(context()+0x6c),2);
    allocation=goodix_mem_malloc(696);put(context()+0x70,(uint32_t)(uintptr_t)allocation);
    if (!allocation) return GX_HRV_ALGO_OUT_OF_MEM;
    (void)memset(allocation,0,696);put(word(context()+0x70),20);
    p=context();put(word(p+0x70)+4,7);
    put(word(p+0x70)+0x294,(uint32_t)((int32_t)word(p+8)/4));
    put(word(p+0x70)+0x298,word(p+8)<<1);put(word(p+0x70)+0x2a4,16);
    put(word(p+0x70)+0x2ac,UINT32_C(0x3f800000));put(word(p+0x70)+0x2b0,UINT32_C(0x3f800000));
    rate=word(p+8);put(p+0x104,rate<<2);put(p+0x108,rate);
    *(volatile float *)(p+0xe8)=(float)(int32_t)word(cfg+8)/10000.0f;
    *(volatile float *)(p+0xec)=(float)(int32_t)word(cfg+12)/10000.0f;
    *(volatile float *)(p+0xf4)=(float)(int32_t)word(cfg+16)/10000.0f;
    *(volatile float *)(p+0xf0)=(float)(int32_t)word(cfg+20)/10000.0f;
    return GX_HRV_ALGO_OK;
}
