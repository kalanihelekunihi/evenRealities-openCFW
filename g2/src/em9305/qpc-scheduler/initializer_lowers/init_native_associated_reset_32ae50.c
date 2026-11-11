#include <stdint.h>

/* Native 0x32ae50..0x32ae6a: clear the associated record's fields at +224,
 * +220 and +218 and the two global halfwords at 0x80568c and 0x805690. */
void opencfw_em9305_associated_reset_32ae50(uintptr_t record)
{
    *(volatile uint32_t *)(record+224u)=0u;
    *(volatile uint8_t *)(record+220u)=0u;
    *(volatile uint16_t *)(record+218u)=0u;
    *(volatile uint16_t *)(uintptr_t)0x80568cu=0u;
    *(volatile uint16_t *)(uintptr_t)0x805690u=0u;
}
