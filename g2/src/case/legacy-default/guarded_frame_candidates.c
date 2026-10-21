/* SPDX-License-Identifier: MIT
 * Stock 0x080035d4 and 0x080039e4 recursion guards. The two transport
 * children remain explicitly imported. Their return register is preserved.
 */
#include <stdint.h>
extern uint32_t case_legacy_ee_transport(uint32_t selector,void *response,uint32_t count);
extern uint32_t case_legacy_pmic_transport(uint32_t selector,uint32_t value);
uint32_t case_legacy_ee_first(uint32_t selector,void *response,uint32_t count)
{
    volatile uint8_t *const guard=(volatile uint8_t *)(uintptr_t)0x20000029u;
    if(*guard!=0u) return selector;
    *guard=1u;
    (void)case_legacy_ee_transport(selector,response,count);
    *guard=0u;
    return 0u;
}
uint32_t case_legacy_pmic_set(uint32_t selector,uint32_t value)
{
    volatile uint8_t *const guard=(volatile uint8_t *)(uintptr_t)0x20000029u;
    if(*guard!=0u) return selector;
    *guard=1u;
    (void)case_legacy_pmic_transport(selector,value);
    *guard=0u;
    return 0u;
}
