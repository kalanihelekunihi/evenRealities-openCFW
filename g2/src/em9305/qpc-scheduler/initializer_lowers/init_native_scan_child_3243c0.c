#include <stdint.h>

/* Native 0x3243c0..0x3243dc: serialize the two six-byte addresses held as
 * {low,high} word pairs at source+0 and source+8 into output+0 and
 * output+6; returns the 12 bytes written. */
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t,uint32_t,uint32_t);

uint32_t opencfw_em9305_scan_prepare_3243c0(uintptr_t output,uintptr_t source)
{
    (void)opencfw_em9305_radio_address_write_3045e8(output,
        *(volatile uint32_t *)source,*(volatile uint32_t *)(source+4u));
    (void)opencfw_em9305_radio_address_write_3045e8(output+6u,
        *(volatile uint32_t *)(source+8u),*(volatile uint32_t *)(source+12u));
    return 12u;
}
