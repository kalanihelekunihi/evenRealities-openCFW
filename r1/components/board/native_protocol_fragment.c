/* R1 0x32408: the extra empty fragment for exact239-byte multiples is native.
 * CRC precedes the length guard; callback status is deliberately ignored.
 * Callback-slot initialization and delivery remain separate evidence gates. */
#include <stdint.h>
#include <stddef.h>
#include "../../source/include/r1_stock_checksums.h"
extern void *memmove(void *,const void *,size_t);
extern volatile uintptr_t r1_fragment_send_callback;
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
typedef uint32_t (*fragment_callback)(uint32_t,void *,uint32_t,uintptr_t);
const char r1_fragment_large_ring[] __attribute__((section(".r1.fragment.large_ring")))="[pb.tran]length error %d  max is %d";
const char r1_fragment_large_sdk[] __attribute__((section(".r1.fragment.large_sdk")))="length error %d  max is %d";
const char r1_fragment_remaining_ring[] __attribute__((section(".r1.fragment.remaining_ring")))="[pb.tran]length != 0 (%d)";
const char r1_fragment_remaining_sdk[] __attribute__((section(".r1.fragment.remaining_sdk")))="length != 0 (%d)";
uint32_t r1_fragment_message(uint32_t handle,const void *payload,uint32_t length)
{
    uint8_t packet[244];
    uint32_t crc=0;
    r1_stock_crc32_update(payload,length,&crc);
    if(length>4096) {
        if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x04800000,r1_fragment_large_ring,r1_fragment_large_ring,length,4096u);
        if(r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_2(0x001c0001,r1_fragment_large_sdk,length,4096u);
        return UINT32_MAX;
    }
    uint32_t remaining=length,total=(uint8_t)(length/239u);
    for(int32_t counter=(int32_t)total;counter>=0;counter=(int16_t)(counter-1)) {
        packet[0]=(uint8_t)counter;
        packet[1]=(uint8_t)crc;packet[2]=(uint8_t)(crc>>8);
        packet[3]=(uint8_t)(crc>>16);packet[4]=(uint8_t)(crc>>24);
        uint32_t count=remaining<239u?remaining:239u;
        if(remaining) (void)memmove(packet+5,(const uint8_t *)payload+(total-(uint32_t)counter)*239u,count);
        uintptr_t callback=r1_fragment_send_callback;
        (void)((fragment_callback)callback)(handle,packet,(uint16_t)(count+5u),callback);
        remaining=(uint16_t)(remaining-count);
    }
    if(remaining) {
        if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x04400000,r1_fragment_remaining_ring,r1_fragment_remaining_ring,remaining);
        if(r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_1(0x001c0001,r1_fragment_remaining_sdk,remaining);
        return UINT32_MAX;
    }
    return 0;
}
