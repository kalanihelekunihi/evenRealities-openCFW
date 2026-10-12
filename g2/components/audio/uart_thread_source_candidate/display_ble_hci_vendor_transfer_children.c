/* Native vendor transfer descriptor guard 0x55c1e0 and control encoder
 * 0x55bce8. ROM words 0x55cc10/0x55c514 authenticate masks. */
#include <stdint.h>

static uint32_t load32(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}

uint32_t audio_ble_vendor_transfer_guard_55c1e0(const uint8_t *row,
                                                 const uint8_t *descriptor,
                                                 uint32_t strict) {
    uint32_t size=load32(descriptor+4u);
    if(size>=6u)return 6u;
    uint32_t disallowed_low=size>=4u?0u:(0xffffffffu<<(size*8u));
    uint32_t disallowed_high=size<4u?0xffffffffu:(0xffffffffu<<((size-4u)*8u));
    uint32_t length=load32(descriptor+16u);
    uint32_t type=load32(descriptor+20u);
    if((disallowed_low&load32(descriptor+8u))!=0u||
       (disallowed_high&load32(descriptor+12u))!=0u)return 6u;
    if(length!=0u&&((uint8_t)type!=0u&&load32(descriptor+28u)==0u))return 6u;
    if(length!=0u&&((uint8_t)type!=1u&&load32(descriptor+24u)==0u))return 6u;
    if(row[8u]==1u) {
        if(length>=0x1000u)return 6u;
    } else if(row[8u]==0u) {
        if(load32(descriptor)>=5u||length>=0x1000u)return 6u;
    }
    if(strict==0u) {
        if((load32(descriptor+36u)&0xe0u)!=0u)return 6u;
        if((load32(descriptor+40u)&0x00e0e0e0u)!=0u)return 6u;
    }
    return 0u;
}

uint32_t audio_ble_vendor_transfer_encode_55bce8(uint32_t slot,uint32_t type,
                                                   uint32_t bool_bit,uint32_t unused,
                                                   uint32_t width,uint32_t unused2,
                                                   uint32_t index,uint32_t count) {
    (void)unused;(void)unused2;
    uint32_t result=((slot&3u)<<20u)|(0x000fff00u&(count<<8u));
    result|=(type==1u)?2u:1u;
    return result|((bool_bit&1u)<<7u)|(width<<24u)|((index&7u)<<4u);
}
