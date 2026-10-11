/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800497c flash option erase executor and busy arbitration.
 */
#include <stdint.h>
extern uint32_t case_boot_option_wait(uint32_t); /* 0x3f6c */
extern void case_boot_option_mass_erase(uint32_t); /* 0x3e94 */
extern void case_boot_option_page_erase(uint32_t,uint32_t); /* 0x3eec */
uint32_t case_boot_option_erase_execute(uint32_t operation,uint32_t *error)
{
    volatile uint8_t *busy=(volatile uint8_t *)(uintptr_t)0x20000f98u;
    if(*busy==1u)return 2u;
    *busy=1u;
    *(volatile uint32_t *)(uintptr_t)0x20000f9cu=0u;
    uint32_t result=case_boot_option_wait(1000u);
    if(result!=0u){*busy=0u;return result;}
    volatile const uint32_t *op=(volatile const uint32_t *)(uintptr_t)operation;
    if(op[0u]==4u){
        case_boot_option_mass_erase(op[1u]);
        result=case_boot_option_wait(1000u);
        *busy=0u;
        return result;
    }
    *error=0xffffffffu;
    uint32_t index=op[2u];
    while(index<op[2u]+op[3u]){
        case_boot_option_page_erase(op[1u],index);
        result=case_boot_option_wait(1000u);
        if(result!=0u){*error=index;break;}
        ++index;
    }
    volatile uint32_t *cr=(volatile uint32_t *)(uintptr_t)0x40022014u;
    *cr&=~2u;
    *busy=0u;
    return result;
}
