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
/* Dedup (0x080039e4): case_legacy_pmic_set is an alias of case_init_pmic_reset (startup/application_init_pmic_write_candidate.c). */
extern uint32_t case_legacy_pmic_set(uint32_t selector,uint32_t value);
/* Dedup (0x080035d4): case_init_pmic_read (was startup/application_boot_pmic_read_candidate.c). */
uint32_t case_init_pmic_read(uint32_t selector,uint8_t *out,uint32_t count) __attribute__((alias("case_legacy_ee_first")));
