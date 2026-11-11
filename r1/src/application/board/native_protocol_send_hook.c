/* Stock0x827f8: load the live hook once and forward the public three arguments.
 * Native r3 contains the branch target as an instruction side effect; the
 * registered C fragment sender has a three-argument signature. */
#include <stdint.h>
typedef uint32_t (*r1_protocol_send_fn)(uint32_t,const void *,uint32_t);
volatile uintptr_t r1_protocol_send_hook
    __attribute__((section(".r1.protocol.send_hook"))) = 0;
uint32_t r1_protocol_send_hook_call(uint32_t handle,const void *packet,uint32_t length)
{
    uintptr_t callback=r1_protocol_send_hook;
    if(callback)return ((r1_protocol_send_fn)callback)(handle,packet,length);
    return UINT32_MAX;
}
