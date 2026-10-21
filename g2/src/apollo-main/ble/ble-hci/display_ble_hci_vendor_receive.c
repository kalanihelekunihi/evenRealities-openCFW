/* Native vendor FIFO receive 0x55cc1c. The 0x55cf38 ROM slot authenticates
 * MMIO 0x40050000; 0x55d278/27c authenticate signature/wait limit. */
#include <stdint.h>

extern uint32_t audio_ble_vendor_transfer_guard_55c1e0(const uint8_t *,const uint8_t *,uint32_t);
extern uint32_t audio_ble_vendor_transfer_encode_55bce8(uint32_t,uint32_t,uint32_t,uint32_t,
                                                         uint32_t,uint32_t,uint32_t,uint32_t);
extern int32_t audio_ble_vendor_wait_480826(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void audio_ble_vendor_yield_4807a0(uint32_t);
extern int32_t audio_ble_vendor_finish_55bd70(uint32_t,uint32_t);
extern void audio_ble_vendor_recover_55bdac(uint8_t *,uint32_t);

static uint32_t get(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static void put(uint8_t *p,uint32_t v) {__builtin_memcpy(p,&v,4u);}
static uint32_t mmio(const volatile uint8_t *p,uint32_t off) {
    return *(volatile const uint32_t *)(const void *)(p+off);
}
static void mmio_put(volatile uint8_t *p,uint32_t off,uint32_t value) {
    *(volatile uint32_t *)(void *)(p+off)=value;
}

int32_t audio_ble_vendor_receive_55cc1c(uint8_t *row,uint8_t *descriptor) {
    if(row==0||(get(row)&0x01ffffffu)!=0x01123456u)return 2;
    if(descriptor==0)return 6;
    if(descriptor[20u]>=2u)return 7;
    uint32_t remaining=get(descriptor+16u);
    if(remaining==0u)descriptor[20u]=0u;
    int32_t result=(int32_t)audio_ble_vendor_transfer_guard_55c1e0(row,descriptor,1u);
    if(result!=0)return result;
    if(row[0x82cu]==2u)return 7;
    uint32_t channel=get(row+4u);
    volatile uint8_t *base=(volatile uint8_t *)(uintptr_t)(0x40050000u+channel*0x1000u);
    uint32_t address_low=get(descriptor+8u);
    uint32_t address_high=get(descriptor+12u);
    uint32_t unit=get(descriptor+4u);
    uint32_t type=descriptor[20u];
    uint32_t option=get(descriptor+32u);
    uint32_t timer=get(row+0x860u);
    result=audio_ble_vendor_wait_480826(timer,(uint32_t)(uintptr_t)(row+36u),0xffffffffu,0u,1u);
    if(result!=0)return result;
    result=audio_ble_vendor_wait_480826(timer,(uint32_t)(uintptr_t)(base+0x248u),6u,4u,1u);
    if(result!=0)return result;
    uint32_t saved=mmio(base,0x200u);
    mmio_put(base,0x200u,0u);
    mmio_put(base,0x218u,mmio(base,0x218u)&~1u);
    mmio_put(base,0x208u,0xffffffffu);
    uint32_t transfer=get(descriptor);
    mmio_put(base,0x2c4u,transfer);
    uint32_t slot=row[8u]==0u?transfer:0u;
    mmio_put(base,0x124u,row[8u]==0u?row[0x8a0u+transfer]:0u);
    uint32_t control=audio_ble_vendor_transfer_encode_55bce8(
        slot,type,option!=0u,slot,address_low,address_high,unit,remaining);
    mmio_put(base,0x128u,(address_low>>8u)|(address_high<<24u));
    uint8_t *input=(uint8_t *)(uintptr_t)get(descriptor+28u);
    if(type==1u) {
        mmio_put(base,0x120u,control);
        uint32_t done=0u;
        while(remaining!=0u) {
            uint32_t polls=0u;
            uint32_t ready;
            while((ready=(mmio(base,0x100u)&0xffffffu)>>16u)<4u&&
                  polls<500000u&&(done==0u||remaining<=ready)) {
                audio_ble_vendor_yield_4807a0(1u);
                done=mmio(base,0x204u)&1u;
                ++polls;
            }
            if(ready<4u)break;
            while(ready>=4u&&remaining!=0u) {
                uint32_t value=mmio(base,0x108u);
                ready-=4u;
                if(remaining<4u) {
                    do {
                        *input++=(uint8_t)value;
                        value>>=8u;
                    } while(--remaining!=0u);
                } else {
                    put(input,value);
                    input+=4u;
                    remaining-=4u;
                }
            }
        }
    } else if(type==0u) {
        const uint8_t *output=(const uint8_t *)(uintptr_t)get(descriptor+24u);
        uint32_t ready=(mmio(base,0x100u)&0xffffu)>>8u;
        while(ready>=4u&&remaining!=0u) {
            mmio_put(base,0x10cu,get(output));
            output+=4u;
            ready-=4u;
            remaining=remaining<4u?0u:remaining-4u;
        }
        mmio_put(base,0x120u,control);
        while(remaining!=0u) {
            uint32_t polls=0u;
            uint32_t ready_more;
            uint32_t done=0u;
            while((ready_more=(mmio(base,0x100u)&0xffffu)>>8u)<4u&&
                  (done=(mmio(base,0x204u)&1u))==0u&&polls<500000u) {
                audio_ble_vendor_yield_4807a0(1u);
                ++polls;
            }
            if(done!=0u||ready_more<4u)break;
            while(ready_more>=4u&&remaining!=0u) {
                mmio_put(base,0x10cu,get(output));
                output+=4u;
                ready_more-=4u;
                remaining=remaining<4u?0u:remaining-4u;
            }
        }
    }
    result=audio_ble_vendor_wait_480826(500000u,(uint32_t)(uintptr_t)(base+0x248u),6u,4u,1u);
    if(result==0) {
        result=audio_ble_vendor_finish_55bd70(channel,0u);
        if(result==0&&remaining!=0u)result=1;
    }
    if(result!=0)audio_ble_vendor_recover_55bdac(row,mmio(base,0x204u));
    mmio_put(base,0x208u,0xffffffffu);
    mmio_put(base,0x200u,saved);
    return result;
}
