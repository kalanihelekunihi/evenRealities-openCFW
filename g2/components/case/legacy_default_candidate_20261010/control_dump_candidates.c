/* SPDX-License-Identifier: MIT
 * Fixed-image 0x0800d1bc, 0x0800d218 and 0x08003558 report bodies.
 * Byte values are live register/product data; the AA reader remains imported.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format,...);
extern uint32_t case_legacy_aa_read(uint32_t offset,uint32_t count,void *output); /* 0x08009040 */
extern uint32_t case_legacy_ee_first(uint32_t selector,void *response,uint32_t count);
extern uint32_t case_binary_5e_hex(const uint8_t *bytes,uint32_t count);
uint32_t case_legacy_aa_first(uint32_t prior)
{
    (void)prior;
    const volatile uint8_t *flag=(volatile uint8_t *)(uintptr_t)0x200000bfu;
    uint32_t result=*flag;
    if(*flag==0u) result=case_legacy_logger("0x00-0x07:");
    for(uint32_t i=0;i<8u;++i){
        uint8_t value=0u;
        (void)case_legacy_aa_read(i,1u,&value);
        if(*flag==0u) result=case_legacy_logger("%x ",(uint32_t)value);
    }
    if(*flag==0u) result=case_legacy_logger("\r\n");
    return result;
}
uint32_t case_legacy_aa_second(uint32_t prior)
{
    (void)prior;
    if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u)
        (void)case_legacy_logger("2510: 0x00-0x07:");
    return case_binary_5e_hex((const uint8_t *)(uintptr_t)0x20000090u,8u);
}
uint32_t case_legacy_ab_child(uint32_t prior)
{
    (void)prior;
    const volatile uint8_t *flag=(volatile uint8_t *)(uintptr_t)0x200000bfu;
    uint32_t result=*flag;
    if(*flag==0u) result=case_legacy_logger("PMIC 0x10-0x1B:");
    for(uint32_t selector=16u;selector<=27u;++selector){
        uint8_t value=0u;
        (void)case_legacy_ee_first(selector,&value,1u);
        if(*flag==0u) result=case_legacy_logger("%x ",(uint32_t)value);
    }
    if(*flag==0u) result=case_legacy_logger("\r\n");
    return result;
}
