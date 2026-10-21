/* Native vendor stack start 0x55c32e. 0x55c548 -> 0x40050000 MMIO,
 * and native 0x55cf34 supplies authenticated control word 0x800040. */
#include <stdint.h>
extern int32_t audio_ble_vendor_stack_start_guard_55bd2e(uint32_t,uint32_t);
extern int32_t audio_ble_vendor_stack_dma_prepare_55c0dc(void *,uint32_t,uint32_t);
extern int32_t audio_ble_vendor_wait_480826(uint32_t,const void *,uint32_t,uint32_t,...);
static uint32_t get(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static void put(uint8_t *p,uint32_t v) {__builtin_memcpy(p,&v,4u);}
static volatile uint32_t *reg(uint32_t index,uint32_t offset) {
    return (volatile uint32_t *)(uintptr_t)(0x40050000u+index*0x1000u+offset);
}

uint64_t audio_ble_radio_stack_start_body(void *record,uint32_t unused,
                                           uint32_t high,uint32_t fourth) {
    (void)unused;
    uint8_t *row=(uint8_t *)record;
    uint32_t status=0u;
    if(row==0||(get(row)&0x01ffffffu)!=0x01123456u)status=2u;
    else if((get(row)&0x02000000u)!=0u)status=0u;
    else {
        uint32_t index=get(row+4u);
        if(audio_ble_vendor_stack_start_guard_55bd2e(index,row[8u]!=0u)==0)
            status=9u;
        else {
            if(get(row+12u)!=0u) {
                put(row+0x24u,0u);put(row+0x1cu,0u);
                *reg(index,0x238u)=0x800040u;
                put(row+0x854u,0u);row[0x83cu]=0u;
                put(row+0x838u,0u);put(row+0x844u,0u);put(row+0x840u,0u);
                row[0x82cu]=0u;put(row+0x830u,0u);row[0x82du]=1u;
                status=(uint32_t)audio_ble_vendor_stack_dma_prepare_55c0dc(
                    row,get(row+16u),get(row+12u));
                *reg(index,0x210u)=2u;
            }
            if(status==0u) {
                high=1u;
                status=(uint32_t)audio_ble_vendor_wait_480826(
                    1000u,(const void *)reg(index,0x248u),6u,4u,1u,fourth);
                if(status==0u)put(row,get(row)|0x02000000u);
                else {
                    *reg(index,0x11cu)&=~1u;
                    *reg(index,0x11cu)&=~0x10u;
                }
            }
        }
    }
    return ((uint64_t)high<<32)|status;
}
__attribute__((naked)) uint64_t audio_ble_radio_stack_start_55c32e(void *record) {
    __asm volatile("b audio_ble_radio_stack_start_body");
}
