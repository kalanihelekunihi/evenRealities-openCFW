/* SPDX-License-Identifier: MIT
 * Stock 0x08009040 retrying control-register read wrapper.
 * The 0x080004c0 serial transaction is an explicit device lower.
 */
#include <stdint.h>
extern uint32_t case_bus_input_transaction(uint32_t command,uint32_t index,
                                            uint32_t count,void *output);
extern uint32_t case_legacy_logger(const char *format,...);
uint32_t case_legacy_aa_read(uint32_t index,uint32_t count,void *output)
{
    volatile uint32_t *diagnostics=(volatile uint32_t *)(uintptr_t)0x2000007cu;
    for(uint32_t retry=1u;retry<10u;++retry){
        __asm__ volatile("cpsid i" ::: "memory");
        uint32_t result=case_bus_input_transaction(0x42u,index,count,output);
        __asm__ volatile("cpsie i" ::: "memory");
        if(result!=0u)return result;
        diagnostics[1]+=1u;
    }
    for(uint32_t i=0;i<count;++i)((uint8_t *)output)[i]=0xffu;
    if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u)
        (void)case_legacy_logger("read failed--retry number=%d,error_location_2510 is %d,read_bit_2510_error1==%d, read_bit_2510_error2==%d\r\n",10u,diagnostics[2],diagnostics[3],diagnostics[4]);
    return 0u;
}
