#include <stdint.h>

/* Native 0x316968..0x316982: increment the scan counter byte at 0x805b01
 * inside a critical section. */
extern uint32_t opencfw_em9305_wsf_critical_enter(void);
extern uint32_t opencfw_em9305_wsf_critical_exit(void);

void opencfw_em9305_scan_counter_up_316968(void)
{
    (void)opencfw_em9305_wsf_critical_enter();
    uint32_t count=*(volatile uint8_t *)0x805b01u;
    *(volatile uint8_t *)0x805b01u=(uint8_t)(count+1u);
    (void)opencfw_em9305_wsf_critical_exit();
}
