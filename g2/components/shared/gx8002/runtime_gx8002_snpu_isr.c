/* SPDX-License-Identifier: MIT */
/* Recovered ISR dispatch boundary. Preserve observed r0 on both paths. */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_snpu_isr_state;
extern int open_cfw_gx8002_snpu_process_status(void);
int open_cfw_gx8002_snpu_isr(int irq, void *private_data)
{
    (void)irq;
    (void)private_data;
    uint32_t state=open_cfw_gx8002_snpu_isr_state;
    if (state==2)
        return 2;
    return open_cfw_gx8002_snpu_process_status();
}
