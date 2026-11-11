#include <stdint.h>
#include <string.h>
#include "goodix_mem.h"
#include "goodix_nadt.h"
#include "native_nadt_state.h"
volatile uint8_t r1_goodix_native_nadt_configuration[120] __attribute__((section(".r1.goodix.native.nadt.configuration"),aligned(4)));
#define B(p,o) (*(volatile uint8_t *)((uintptr_t)(p)+(o)))
#define H(p,o) (*(volatile uint16_t *)((uintptr_t)(p)+(o)))
#define W(p,o) (*(volatile uint32_t *)((uintptr_t)(p)+(o)))
static float scaled(const void *p,float factor)
{
    float input=(float)(int32_t)W(p,0x2c);
    float product=input*factor;
    return product/1000.0f;
}
/* Inputs are finite and bounded by int32_t * 15 / 1000. Native unsigned
 * conversion saturates negatives and raises IOC below -1; a C cast there
 * would be undefined. The volatile division raises IOC without assembly. */
static uint32_t unsigned_scaled(float value)
{
    union {float f;uint32_t u;} bits={value};
    if ((bits.u>>31) && (bits.u&0x7fffffffu)>=0x3f800000u) {
        volatile float zero=0.0f;
        volatile float invalid=zero/zero;
        (void)invalid;
        return 0;
    }
    return (uint32_t)value;
}
uint32_t r1_goodix_native_nadt_configure(const void *p)
{
    volatile uint8_t *out=r1_goodix_native_nadt_configuration;
    uint32_t status=0,rate=H(p,0),mode;
    if(rate!=25 && rate!=50 && rate!=100 && rate!=200){rate=25;status=3;}
    H(out,0)=rate;
    mode=B(p,2);
    if(mode<1 || mode>3){mode=1;status=3;}
    B(out,2)=mode;
    H(out,4)=H(p,4); B(out,6)=1;
    B(out,7)=B(p,6); B(out,8)=B(p,7);
    W(out,0xc)=W(p,8)-0x800000u; W(out,0x10)=W(p,0xc)-0x800000u;
    W(out,0x14)=W(p,0x10); W(out,0x18)=1;
    W(out,0x1c)=0x3c23d70a; W(out,0x20)=0x3ca3d70a;
    B(out,0x24)=B(p,0x14); W(out,0x28)=8; W(out,0x2c)=W(p,0x18);
    W(out,0x30)=(int32_t)scaled(p,2.0f);
    H(out,0x34)=60; H(out,0x36)=40;
    W(out,0x38)=(int32_t)scaled(p,6.0f);
    H(out,0x3c)=H(p,0x1c); H(out,0x3e)=H(p,0x1e);
    W(out,0x40)=W(p,0x20); W(out,0x44)=(int32_t)W(p,0x20)/2;
    B(out,0x48)=B(p,0x24);
    H(out,0x4a)=unsigned_scaled(scaled(p,5.0f)); H(out,0x4c)=900;
    H(out,0x4e)=unsigned_scaled(scaled(p,3.0f));
    H(out,0x50)=unsigned_scaled(scaled(p,7.0f));
    B(out,0x52)=1; H(out,0x54)=10; H(out,0x56)=H(p,0x26);
    if(!H(p,0x26)) B(out,0x52)=0;
    W(out,0x58)=W(p,0x28)<<1; W(out,0x5c)=W(p,0x28);
    H(out,0x60)=unsigned_scaled(scaled(p,15.0f)); H(out,0x62)=900;
    H(out,0x64)=unsigned_scaled(scaled(p,6.0f));
    B(out,0x66)=5; B(out,0x67)=B(p,0x30);
    H(out,0x68)=H(p,0x32); H(out,0x6a)=H(p,0x32);
    B(out,0x6c)=B(p,0x34); B(out,0x6d)=B(p,0x35);
    H(out,0x6e)=H(p,0x36); H(out,0x70)=H(p,0x38); H(out,0x72)=H(p,0x3a);
    H(out,0x74)=70;
    return status;
}

/* Stock entry 0x6e664 tails into configure at 0x73e2c. Invalid rate/mode
 * leaves the allocation and reset state live, exactly as the native caller. */
goodix_nadt_ret goodix_nadt_init(const void *configuration,int32_t size,
    const char *interface_version)
{
    if (!configuration || size!=60 || strcmp(interface_version,"pv_v1.0.0"))
        return GX_ALGO_NADT_RWONG_INPUT;
    void *allocation=goodix_mem_malloc(52);
    r1_goodix_native_nadt_reset_fields(allocation,1);
    r1_goodix_native_nadt_state.flags[0]=0xbf;
    return (goodix_nadt_ret)r1_goodix_native_nadt_configure(configuration);
}
