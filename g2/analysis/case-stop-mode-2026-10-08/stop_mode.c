/* Independent locked-image reconstruction of080050e8..0800511e.
 * This is an offline comparison module, not a firmware power-management patch.
 * Raw register arguments preserve the stock callee's full32-bit comparison. */
#include <stdint.h>
#define CR1 (*(volatile uint32_t *)0x40007000u)
#define SCR (*(volatile uint32_t *)0xe000ed10u)
void case_stop_mode(uint32_t regulator,uint32_t entry) {
 CR1=(CR1 & ~7u) | (regulator!=0u ? 1u : 0u);
 SCR=SCR | 4u;
 if(entry==1u) __asm volatile("wfi" ::: "memory");
 else __asm volatile("sev\n wfe\n wfe" ::: "memory");
 SCR=SCR & ~4u;
}
