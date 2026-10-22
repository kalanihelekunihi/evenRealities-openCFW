/* SPDX-License-Identifier: MIT
 * Stock 0x08009004 ten-attempt one-byte frame writer. Caller R2 is the
 * byte pointer, forwarded as R3 to 0x0800056c; observed in instructions.
 */
#include <stdint.h>
extern void case_bus_output_prepare(void); /* 0x0800a2e6 */
extern uint32_t case_bus_write_transaction(uint32_t marker,uint32_t code,
                                            uint32_t count,const uint8_t *bytes); /* 0x0800056c */
/* Stock 0x08009004 (gls_frame_pack_r) */
uint32_t case_watchdog_frame_pack(uint32_t code,uint32_t count,const uint8_t *bytes)
{
    volatile uint32_t *attempts=(volatile uint32_t *)(uintptr_t)0x20000000u;
    for(uint32_t retry=1u;retry<10u;++retry){
        __asm__ volatile("cpsid i" ::: "memory");
        case_bus_output_prepare();
        uint32_t result=case_bus_write_transaction(0x5au,code,count,bytes);
        __asm__ volatile("cpsie i" ::: "memory");
        if(result!=0u)return result;
        *attempts+=1u;
    }
    return 0u;
}
