#include <stdint.h>
extern uint32_t r1_protocol_send_response(uint32_t,const void *,const void *,uint32_t);
/* Native0x84c0c with ordinary C results. Current C callers consume R0;
 * wrappers that expose saved scratch words restore their own values. */
__attribute__((noinline)) uint32_t r1_protocol_response_send_0x100(uint32_t handle,uint32_t operation,uint32_t first,uint32_t second,const void *payload,uint32_t length)
{
    volatile uint32_t header[2]={first,second};
    uint32_t result=0;
    if (handle!=0xffffu) {
        header[0]=((first^1u)|2u)&255u;
        header[0]|=0x100u|(((operation>>8)&255u)<<16)|((operation&255u)<<24);
        header[1]=(uint16_t)second;
        result=r1_protocol_send_response(handle,(const void *)header,payload,length)==0;
    }
    return result;
}
