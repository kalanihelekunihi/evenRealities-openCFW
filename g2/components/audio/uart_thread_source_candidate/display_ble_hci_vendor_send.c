/* Native vendor FIFO transfer 0x55cf40. ROM 0x55d248/278/27c authenticate
 * MMIO 0x40050000, row signature 0x01123456, and wait limit 500000. */
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

int32_t audio_ble_vendor_send_55cf40(uint8_t *row,uint8_t *descriptor) {
    if(row==0||(get(row)&0x01ffffffu)!=0x01123456u)return 2;
    if(descriptor==0)return 6;
    if((uint8_t)get(descriptor+20u)!=2u)return 7;
    int32_t result=(int32_t)audio_ble_vendor_transfer_guard_55c1e0(row,descriptor,1u);
    if(result!=0)return result;
    if(row[0x82cu]==2u)return 7;
    uint32_t channel=get(row+4u);
    volatile uint8_t *base=(volatile uint8_t *)(uintptr_t)(0x40050000u+channel*0x1000u);
    uint32_t transfer=get(descriptor);
    uint32_t address_low=get(descriptor+8u);
    uint32_t address_high=get(descriptor+12u);
    uint32_t unit=get(descriptor+4u);
    uint32_t receive_remaining=get(descriptor+16u);
    uint32_t transmit_remaining=receive_remaining;
    uint32_t type=get(descriptor+20u);
    uint32_t option=get(descriptor+32u);
    uint8_t *input=(uint8_t *)(uintptr_t)get(descriptor+28u);
    const uint8_t *output=(const uint8_t *)(uintptr_t)get(descriptor+24u);
    uint32_t timer=get(row+0x860u);
    result=audio_ble_vendor_wait_480826(timer,(uint32_t)(uintptr_t)(row+36u),0xffffffffu,0u,1u);
    if(result!=0)return result;
    result=audio_ble_vendor_wait_480826(timer,(uint32_t)(uintptr_t)(base+0x248u),6u,4u,1u);
    if(result!=0)return result;
    uint32_t saved=mmio(base,0x200u);
    mmio_put(base,0x200u,0u);
    mmio_put(base,0x218u,mmio(base,0x218u)&~1u);
    mmio_put(base,0x208u,0xffffffffu);
    mmio_put(base,0x2c4u,transfer);
    mmio_put(base,0x124u,(mmio(base,0x124u)&~0x1fu)|
                         (row[0x8a0u+transfer]&0xfu)|0x10u);
    uint32_t slot=row[8u]==0u?transfer:0u;
    uint32_t control=audio_ble_vendor_transfer_encode_55bce8(
        slot,(uint8_t)type,option!=0u,slot,address_low,address_high,unit,receive_remaining);
    mmio_put(base,0x128u,(address_low>>8u)|(address_high<<24u));
    mmio_put(base,0x280u,mmio(base,0x280u)|4u);
    mmio_put(base,0x120u,control);
    uint32_t done=0u;
    while(done==0u&&(receive_remaining!=0u||transmit_remaining!=0u)) {
        uint32_t ready_tx=(mmio(base,0x100u)&0xffffu)>>8u;
        uint32_t ready_rx=(mmio(base,0x100u)&0xffffffu)>>16u;
        uint32_t polls=0u;
        while(ready_tx<4u&&ready_rx<4u&&polls<500000u&&
              (done==0u||ready_rx>=receive_remaining)) {
            audio_ble_vendor_yield_4807a0(1u);
            done=mmio(base,0x204u)&1u;
            ready_tx=(mmio(base,0x100u)&0xffffu)>>8u;
            ready_rx=(mmio(base,0x100u)&0xffffffu)>>16u;
            ++polls;
        }
        if(ready_tx<4u&&ready_rx<4u)break;
        while(ready_tx>=4u&&transmit_remaining!=0u) {
            uint32_t value=get(output);
            mmio_put(base,0x10cu,value);
            output+=4u;
            ready_tx-=4u;
            transmit_remaining=transmit_remaining<4u?0u:transmit_remaining-4u;
        }
        while(ready_rx>=4u&&receive_remaining!=0u) {
            uint32_t value=mmio(base,0x108u);
            ready_rx-=4u;
            if(receive_remaining<4u) {
                do {
                    *input++=(uint8_t)value;
                    value>>=8u;
                } while(--receive_remaining!=0u);
            } else {
                put(input,value);
                input+=4u;
                receive_remaining-=4u;
            }
        }
    }
    result=audio_ble_vendor_wait_480826(500000u,(uint32_t)(uintptr_t)(base+0x248u),6u,4u,1u);
    if(result==0) {
        result=audio_ble_vendor_finish_55bd70(channel,0u);
        if(result==0&&(receive_remaining!=0u||transmit_remaining!=0u))result=1;
        else if(result!=0)audio_ble_vendor_recover_55bdac(row,mmio(base,0x204u));
        mmio_put(base,0x208u,0xffffffffu);
        mmio_put(base,0x200u,saved);
    }
    mmio_put(base,0x280u,mmio(base,0x280u)&~4u);
    return result;
}
