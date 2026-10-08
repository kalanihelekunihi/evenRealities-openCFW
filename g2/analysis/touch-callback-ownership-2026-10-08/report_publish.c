/* Reconstruction of the publish slice at 0x3c18..0x3c36 only.
 * Report construction, logging and following state writes are outside this API.
 * Storage is borrowed static RAM: this function does not allocate or transfer
 * ownership. The caller must serialize publication with I2C access. */
#include "cy_scb_i2c.h"
#include "ownership.h"
void touch_report_publish_slice(void) {
 uint32_t *src=(uint32_t *)0x20000990u;
 uint32_t *dst=(uint32_t *)0x200009b0u;
 uint32_t a=src[0],b=src[1],c=src[2];
 dst[0]=a; dst[1]=b; dst[2]=c; dst[3]=src[3];
 Cy_SCB_I2C_SlaveConfigReadBuf(SCB1,(uint8_t *)dst,16,
                             (cy_stc_scb_i2c_context_t *)0x200008ecu);
 *(volatile uint32_t *)0x40040444u=1u; /* P4.0 DR_CLR: attention asserted */
}
