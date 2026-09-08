/* SPDX-License-Identifier: MIT */
/* IRQ15 callback at package0x15ad4. Register names are deliberately avoided
 * until independently documented; the observed conditional reads are exact. */
#include <stdint.h>
int open_cfw_gx8002_flash_interrupt(int irq,void *private_data)
{
    (void)irq;
    (void)private_data;
    volatile uint32_t *controller=(volatile uint32_t *)0xa2000000u;
    unsigned status=controller[0x30/4];
    if (status&2u) (void)controller[0x38/4];
    if (status&8u) (void)controller[0x3c/4];
    return 0;
}
