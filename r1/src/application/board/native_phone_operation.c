#include <stdint.h>
extern uint32_t r1_phone_connection_handle_get(void);
extern uint32_t r1_protocol_response_send_0x100(uint32_t,uint32_t,uint32_t,uint32_t,const void *,uint32_t);
/* Native0x83896 saves incoming r2/r3. Null input returns0 with those words
 * intact; otherwise the words become the payload pointer and literal7. The
 * selected common consumer only reads its two incoming stack arguments. */
__attribute__((noinline)) uint32_t r1_phone_cmd_send_op1(const void *payload,uint32_t first,uint32_t second)
{
    uint32_t incoming3;
    __asm__ volatile("mov %0, r3" : "=r"(incoming3));
    volatile uint32_t saved2=second,saved3=incoming3;
    uint32_t result=0;
    if (payload) {
        uint32_t handle=r1_phone_connection_handle_get();
        saved2=(uint32_t)(uintptr_t)payload;saved3=7;
        result=r1_protocol_response_send_0x100(handle,1,first,second,payload,7);
    }
    uint32_t restored2=saved2,restored3=saved3;
    __asm__ volatile("mov r2, %0\nmov r3, %1" : : "r"(restored2),"r"(restored3) : "r2","r3");
    return result;
}
