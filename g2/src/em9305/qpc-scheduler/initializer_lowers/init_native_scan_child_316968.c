#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x316968..0x316982: increment the scan counter byte at ((uintptr_t)&em9305_ram_805af0 + 0x11u)
 * inside a critical section. */
extern uint32_t opencfw_em9305_wsf_critical_enter(void);
extern uint32_t opencfw_em9305_wsf_critical_exit(void);

void opencfw_em9305_scan_counter_up_316968(void)
{
    (void)opencfw_em9305_wsf_critical_enter();
    uint32_t count=*(volatile uint8_t *)((uintptr_t)&em9305_ram_805af0 + 0x11u);
    *(volatile uint8_t *)((uintptr_t)&em9305_ram_805af0 + 0x11u)=(uint8_t)(count+1u);
    (void)opencfw_em9305_wsf_critical_exit();
}
