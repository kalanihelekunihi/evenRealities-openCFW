/* 0x83448: a null registration fails without clearing the previous callback.
 * Native caller-saved r1/r2/r3 values are retained as an observed ABI contract. */
#include <stdint.h>
extern volatile uintptr_t r1_protocol_send_hook;
uint32_t r1_protocol_send_callback_set(uintptr_t callback)
{
    register uintptr_t word1 __asm__("r1");
    register uint32_t word2 __asm__("r2"),word3 __asm__("r3");
    __asm__ volatile("" : "+r"(word1), "+r"(word2), "+r"(word3));
    register uint32_t result __asm__("r0")=UINT32_MAX;
    if(callback) {
        r1_protocol_send_hook=callback;
        word1=(uintptr_t)&r1_protocol_send_hook;
        result=0;
    }
    __asm__ volatile("" : "+r"(result), "+r"(word1), "+r"(word2), "+r"(word3));
    return result;
}
