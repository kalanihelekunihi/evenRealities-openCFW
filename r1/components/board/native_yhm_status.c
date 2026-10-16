#include <stdint.h>
extern uint32_t r1_yhm_ready_native(void);
extern uint32_t r1_yhm_register_read_native(uint32_t,uint32_t,uint8_t *);
/* Native0x3529a saves incoming r3 as its read word and restores that word to
 * r3 on return. Explicit register moves preserve its nonstandard boundary. */
__attribute__((noinline)) uint32_t r1_yhm_status_native(void)
{
    uint32_t incoming;
    __asm__ volatile("mov %0, r3" : "=r"(incoming));
    volatile uint32_t word=incoming;
    uint32_t result=12;
    if (r1_yhm_ready_native()) {
        (void)r1_yhm_register_read_native(6,1,(uint8_t *)&word);
        uint32_t status=((const volatile uint8_t *)&word)[0]>>4;
        result=status==14 ? 17 : status;
    }
    uint32_t restored=word;
    __asm__ volatile("mov r3, %0" : : "r"(restored) : "r3");
    return result;
}
