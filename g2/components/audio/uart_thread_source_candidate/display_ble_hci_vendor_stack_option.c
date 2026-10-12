/* Native vendor stack option transfer 0x55c7e8. ROM 0x55d248 ->
 * 0x40050000 vendor MMIO, 0x55cc14 -> 0x01123456 live-row signature. */
#include <stdint.h>
extern void audio_ble_vendor_irq_off_47f5b8(uint32_t);
extern void audio_ble_vendor_irq_on_47f7ae(uint32_t);
extern int32_t audio_ble_vendor_irq_disable_4c44bc(uint32_t,uint32_t);
extern int32_t audio_ble_vendor_irq_enable_4c4530(uint32_t,uint32_t);
extern void audio_ble_vendor_option_before_store_55c13a(void *);
extern void audio_ble_vendor_option_after_load_55c168(void *);
extern int32_t audio_ble_vendor_wait_480826(uint32_t,const void *,uint32_t,uint32_t,...);
static uint32_t get(const uint8_t *p) {uint32_t x;__builtin_memcpy(&x,p,4u);return x;}
static void put(uint8_t *p,uint32_t x) {__builtin_memcpy(p,&x,4u);}
static volatile uint32_t *reg(uint32_t index,uint32_t offset) {
    return (volatile uint32_t *)(uintptr_t)(0x40050000u+index*0x1000u+offset);
}
static const uint16_t row_offsets[13]={0x21bu,0x21du,0x220u,0x221u,0x222u,0x223u,
    0x224u,0x225u,0x226u,0x227u,0x21cu,0x21fu,0x21eu};
static const uint16_t reg_offsets[13]={0x104u,0x118u,0x22cu,0x234u,0x23cu,0x240u,
    0x244u,0x280u,0x2c0u,0x200u,0x210u,0x228u,0x11cu};

uint64_t audio_ble_radio_stack_option_body(void *record,uint32_t option,
                                            uint32_t enabled,uint32_t high) {
    uint8_t *row=(uint8_t *)record;
    uint32_t saved_high=high;
    if(row==0||(get(row)&0x01ffffffu)!=0x01123456u)
        return ((uint64_t)saved_high<<32)|2u;
    uint32_t index=get(row+4u);
    uint8_t op=(uint8_t)option;
    if(op==0u) {
        if((uint8_t)enabled!=0u&&row[0x868u]==0u)
            return ((uint64_t)saved_high<<32)|7u;
        audio_ble_vendor_irq_off_47f5b8((index+3u)&0xffu);
        if((uint8_t)enabled!=0u) {
            for(uint32_t i=0u;i<13u;i++) {
                uint32_t value=get(row+(uint32_t)row_offsets[i]*4u);
                if(row_offsets[i]==0x21fu)value&=~1u;
                *reg(index,reg_offsets[i])=value;
            }
            if((get(row+0x87cu)&1u)!=0u)
                audio_ble_vendor_option_before_store_55c13a(row);
            if((get(row)&0x02000000u)!=0u) {
                saved_high=1u;
                (void)audio_ble_vendor_wait_480826(1000u,(const void *)reg(index,0x248u),6u,4u);
            }
            row[0x868u]=0u;
        }
        return ((uint64_t)saved_high<<32)|
            (uint32_t)audio_ble_vendor_irq_disable_4c44bc(4u,(index+3u)&0xffu);
    }
    if(op!=1u&&op!=2u)return ((uint64_t)saved_high<<32)|6u;
    if((get(row)&0x02000000u)!=0u &&
       (((*reg(index,0x248u)&6u)!=4u)||get(row+0x24u)!=0u))
        return ((uint64_t)saved_high<<32)|3u;
    if((uint8_t)enabled!=0u) {
        for(uint32_t i=0u;i<13u;i++)
            put(row+(uint32_t)row_offsets[i]*4u,*reg(index,reg_offsets[i]));
        if(((*reg(index,0x228u))&1u)!=0u)
            audio_ble_vendor_option_after_load_55c168(row);
        row[0x868u]=1u;
    }
    *reg(index,0x11cu)&=~1u;
    *reg(index,0x11cu)&=~0x10u;
    audio_ble_vendor_irq_on_47f7ae((index+3u)&0xffu);
    return ((uint64_t)saved_high<<32)|
        (uint32_t)audio_ble_vendor_irq_enable_4c4530(4u,(index+3u)&0xffu);
}
__attribute__((naked)) uint64_t audio_ble_radio_stack_option_55c7e8(void *record,
                                                                        uint32_t option,
                                                                        uint32_t enabled) {
    __asm volatile("b audio_ble_radio_stack_option_body");
}
