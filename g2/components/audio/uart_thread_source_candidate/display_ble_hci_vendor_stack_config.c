/* Native vendor stack configure 0x55ca94. ROM constants at 0x55d24c..274
 * and MMIO base 0x55cf38 are authenticated from the stock image. */
#include <stdint.h>
extern uint32_t audio_ble_vendor_clock_divider_55bf64(uint32_t,uint32_t);
static uint32_t get(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static void put(uint8_t *p,uint32_t v) {__builtin_memcpy(p,&v,4u);}
static volatile uint32_t *reg(uint32_t index,uint32_t offset) {
    return (volatile uint32_t *)(uintptr_t)(0x40050000u+index*0x1000u+offset);
}

uint32_t audio_ble_radio_stack_config_55ca94(void *record,const void *configuration) {
    uint8_t *row=(uint8_t *)record;
    if(row==0||(get(row)&0x01ffffffu)!=0x01123456u)return 2u;
    if(configuration==0||get(row+4u)>7u)return 6u;
    if((get(row)&0x02000000u)!=0u)return 7u;
    const uint8_t *cfg=(const uint8_t *)configuration;
    uint32_t index=get(row+4u);
    row[8u]=cfg[0];
    *reg(index,0x104u)=0x1010u;
    uint32_t frequency=get(cfg+4u);
    uint32_t divisor=0x773b2301u;
    if(cfg[0]==0u) {
        if(cfg[8u]>3u||frequency>=0x02dc6c01u)return 6u;
        divisor=audio_ble_vendor_clock_divider_55bf64(frequency,(cfg[8u]&3u)>>1);
        *reg(index,0x280u)=cfg[8u]&3u;
    } else {
        if(cfg[0]!=1u)return 5u;
        if(frequency==0x186a0u) {
            *reg(index,0x2c0u)=0x3f070u;
        } else if(frequency==0x61a80u) {
            *reg(index,0x2c0u)=0x3f270u;
            divisor=0x1d0e2301u;
        } else if(frequency==0xf4240u) {
            *reg(index,0x2c0u)=0x23040u;
            divisor=0x0b052301u;
        } else return 6u;
    }
    *reg(index,0x118u)=divisor|1u;
    put(row+0x864u,0xf4240u/frequency);
    put(row+0x860u,1000u);
    uint32_t count=get(cfg+12u),width=get(cfg+16u);
    put(row+12u,count);put(row+16u,width);
    if(count!=0u) {
        row[0x8a4u]=(uint8_t)((count+width*4u)<0x20080000u);
        uint32_t computed=((width-8u)*4u)/0x60u;
        if(computed>0x100u)computed=0x100u;
        put(row+0x858u,computed);
    }
    for(uint32_t i=0;i<4u;i++)row[0x8a0u+i]=0u;
    return 0u;
}
