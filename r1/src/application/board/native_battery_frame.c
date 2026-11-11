#include <stdint.h>
extern uint32_t r1_glasses_connection_handle_get(void);
extern int32_t r1_ble_tx_queue_dispatch_type0(uint32_t,const void *,uint32_t);
/* Stock packet layout and dispatch behavior with the ordinary C result ABI.
 * Caller-clobbered scratch register restoration is intentionally retired. */
__attribute__((noinline)) uint32_t r1_glasses_tag_frame_send(uint32_t level,uint32_t state)
{
    volatile uint32_t words[3]={0x008b0900u,(uint8_t)level|((uint32_t)(uint8_t)state<<8),0};
    uint32_t result=r1_glasses_connection_handle_get();
    if (result!=0xffffu) {
        uint32_t handle=r1_glasses_connection_handle_get();
        result=(uint32_t)r1_ble_tx_queue_dispatch_type0(handle,(const void *)words,6);
    }
    return result;
}
