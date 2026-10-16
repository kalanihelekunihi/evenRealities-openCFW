#include <stdint.h>
extern uint32_t r1_glasses_connection_handle_get(void);
extern int32_t r1_ble_tx_queue_dispatch_type0(uint32_t,const void *,uint32_t);
/* Native0x913fc uses a zeroed12-byte record and sends only its first6 bytes.
 * The complete three words are restored to r1/r2/r3 on every return. */
__attribute__((noinline)) uint32_t r1_glasses_tag_frame_send(uint32_t level,uint32_t state)
{
    volatile uint32_t words[3]={0x008b0900u,(uint8_t)level|((uint32_t)(uint8_t)state<<8),0};
    uint32_t result=r1_glasses_connection_handle_get();
    if (result!=0xffffu) {
        uint32_t handle=r1_glasses_connection_handle_get();
        result=(uint32_t)r1_ble_tx_queue_dispatch_type0(handle,(const void *)words,6);
    }
    uint32_t restored1=words[0],restored2=words[1],restored3=words[2];
    __asm__ volatile("mov r1, %0\nmov r2, %1\nmov r3, %2" : : "r"(restored1),"r"(restored2),"r"(restored3) : "r1","r2","r3");
    return result;
}
