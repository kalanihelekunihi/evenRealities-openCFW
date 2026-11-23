#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x322bac..0x322c94: set up a new connection record from the
 * connect parameters: mark the procedure (+408 = 12), derive the access
 * address (+412) and its folded CRC seed (+400), copy and transform the
 * channel map (+352/+356), store the interval (+416 = +348 << 8) and the
 * hop byte. When encryption is resumed (+484), copy the stored SKD/IV
 * material (+485 -> +444 with the access address mixed into bytes 0..3,
 * +92 -> +428), set both 0x201 lengths and notify the key hook at
 * *((uintptr_t)&em9305_ram_802878 + 0x48u) with the record's 512-byte slot id + 6. */
extern uint32_t opencfw_em9305_radio_access_mix_3188b8(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_channel_transform_30e3fc(uintptr_t);
extern void *opencfw_em9305_memcpy(void *,const void *,uint32_t);

static uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}
static void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}

void opencfw_em9305_dispatch_child_322bac(uintptr_t record,uintptr_t parameters)
{
    w8(record+408u,12u);
    uint32_t access=opencfw_em9305_radio_access_mix_3188b8(r32(parameters+0x24u),0u);
    uint32_t high=r32(parameters+0x34u);
    uint32_t low=r32(parameters+0x30u);
    w32(record+412u,access);
    w16(record+400u,access^(access>>16));
    w8(record+398u,1u);
    w32(record+356u,high);
    w32(record+352u,low);
    (void)opencfw_em9305_radio_channel_transform_30e3fc(record+352u);
    uint32_t interval=r16(record+348u);
    uint32_t resumed=r8(record+484u);
    w8(record+421u,r8(record+292u));
    w32(record+416u,interval<<8);
    if(resumed==0u) return;
    w8(record+453u,1u);
    w16(record+454u,513u);
    (void)opencfw_em9305_memcpy((void *)(record+444u),(const void *)(record+485u),8u);
    uint32_t b0=r8(record+444u);
    access=r32(record+412u);
    uint32_t b1=r8(record+445u),b2=r8(record+446u),b3=r8(record+447u);
    w8(record+444u,b0^access);
    w8(record+445u,(access>>8)^b1);
    w8(record+446u,(access>>16)^b2);
    w8(record+447u,(access>>24)^b3);
    (void)opencfw_em9305_memcpy((void *)(record+428u),(const void *)(record+92u),16u);
    uintptr_t hook=r32(((uintptr_t)&em9305_ram_802878 + 0x48u));
    w16(record+468u,513u);
    if(hook==0u) return;
    uint32_t slot=(uint8_t)((((uint32_t)record-r32(((uintptr_t)&em9305_ram_805be0 + 0x5cu)))>>9)+6u);
    ((void (*)(uintptr_t,uint32_t,uint32_t))hook)(record+428u,slot,1u);
}
