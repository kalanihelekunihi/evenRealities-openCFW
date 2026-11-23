#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32ae50..0x32ae6a: clear the associated record's fields at +224,
 * +220 and +218 and the two global halfwords at ((uintptr_t)&em9305_ram_805688 + 0x4u) and ((uintptr_t)&em9305_ram_805688 + 0x8u). */
void opencfw_em9305_associated_reset_32ae50(uintptr_t record)
{
    *(volatile uint32_t *)(record+224u)=0u;
    *(volatile uint8_t *)(record+220u)=0u;
    *(volatile uint16_t *)(record+218u)=0u;
    em9305_ram_805688.u16_80568c=0u;
    em9305_ram_805688.u16_805690=0u;
}
