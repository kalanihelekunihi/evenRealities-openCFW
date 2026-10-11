/* SPDX-License-Identifier: MIT
 * Native CASE 0x8fa8 and 0x90ac ten-attempt peripheral reads.
 */
#include <stdint.h>
extern void case_bus_output_prepare(void); /* 0xa2e6 */
extern uint32_t case_motion_input_transaction(uint32_t command,uint32_t index,uint32_t count,uint8_t *out); /* 0x0420 */
extern uint32_t case_bus_config_input_transaction(uint32_t command,uint32_t index,uint32_t count,uint8_t *out); /* 0x0310 */
extern uint32_t case_legacy_logger(const char *format,...);
uint32_t case_init_motion_read(uint32_t index,uint32_t count,uint8_t *out)
{
    volatile uint32_t *diagnostics=(volatile uint32_t *)(uintptr_t)0x20000000u;
    for(uint32_t retry=1u;retry<10u;++retry){
        __asm__ volatile("cpsid i" ::: "memory");
        case_bus_output_prepare();
        uint32_t result=case_motion_input_transaction(0x5au,index,count,out);
        __asm__ volatile("cpsie i" ::: "memory");
        if(result!=0u)return result;
        diagnostics[0]++;
        if(diagnostics[4]==1u)
            (void)case_legacy_logger((const char *)(uintptr_t)0x0800d408u,diagnostics[1],diagnostics[2],diagnostics[3]);
    }
    for(uint32_t i=0u;i<count;++i)out[i]=0xffu;
    return 0u;
}
uint32_t case_init_secondary_config_read(uint32_t index,uint32_t count,uint8_t *out)
{
    volatile uint32_t *diagnostics=(volatile uint32_t *)(uintptr_t)0x2000007cu;
    for(uint32_t retry=1u;retry<10u;++retry){
        __asm__ volatile("cpsid i" ::: "memory");
        uint32_t result=case_bus_config_input_transaction(2u,index,count,out);
        __asm__ volatile("cpsie i" ::: "memory");
        if(result!=0u)return result;
        diagnostics[1]++;
        (void)case_legacy_logger((const char *)(uintptr_t)0x0800d4c0u,retry,diagnostics[2],diagnostics[3],diagnostics[4]);
    }
    for(uint32_t i=0u;i<count;++i)out[i]=0xffu;
    return 0u;
}
