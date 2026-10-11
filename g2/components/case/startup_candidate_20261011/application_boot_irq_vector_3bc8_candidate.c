/* SPDX-License-Identifier: MIT
 * CASE 0x08003bc8 PMIC interrupt branch and acknowledgement. Diagnostic
 * literals are native human-readable text, represented as C strings.
 */
#include <stdint.h>
extern uint32_t case_init_pmic_read(uint32_t reg,uint8_t *out,uint32_t count); /* 0x35d4 */
extern uint32_t case_legacy_logger(const char *format,...); /* 0x9170 */
extern void case_boot_irq_button_refresh(void); /* 0x3a84 */
extern void case_boot_irq_clear(uint32_t mask); /* 0x4d04 */
void case_vector_irq_3bc8(void)
{
    volatile uint32_t *const bus=(volatile uint32_t *)(uintptr_t)0x40021800u;
    if(((bus[3]|bus[4])&1u)!=0u){
        uint8_t value;
        (void)case_init_pmic_read(16u,&value,1u);
        (void)case_init_pmic_read(17u,&value,1u);
    }else{
        if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u){
            (void)case_legacy_logger("2217 int");
            (void)case_legacy_logger("\r\n");
        }
        case_boot_irq_button_refresh();
    }
    case_boot_irq_clear(1u);
    case_boot_irq_clear(2u);
}
