/* R1 2.2.6.0009 0x827f8: callback dispatch, not transport delivery.
 * The fourth callback register contains the loaded callback address.
 * Registration and live callback targets remain separately evidenced seams. */
#include <stdint.h>
typedef uint32_t (*r1_protocol_send_fn)(uint32_t,const void *,uint32_t,uintptr_t);
volatile uintptr_t r1_protocol_send_hook
    __attribute__((section(".r1.protocol.send_hook"))) = 0;
uint32_t r1_protocol_send_hook_call(uint32_t handle,const void *packet,uint32_t length)
{
    uintptr_t callback=r1_protocol_send_hook;
    if(callback) return ((r1_protocol_send_fn)callback)(handle,packet,length,callback);
    register uintptr_t r3 __asm__("r3")=0;
    __asm__ volatile("" : "+r"(r3));
    return UINT32_MAX;
}
