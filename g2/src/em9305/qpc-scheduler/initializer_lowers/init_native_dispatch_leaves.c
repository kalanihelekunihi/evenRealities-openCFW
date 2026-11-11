#include <stdint.h>

/* Native dispatch leaves 0x31cb84, 0x31cb9c and 0x31cba4: store the
 * pending command opcode byte at +200 (0x3d, 8, or the byte at +290). */
void opencfw_em9305_dispatch_leaf_31cb84(uintptr_t record)
{
    *(volatile uint8_t *)(record+200u)=0x3du;
}

void opencfw_em9305_dispatch_leaf_31cb9c(uintptr_t record)
{
    *(volatile uint8_t *)(record+200u)=8u;
}

void opencfw_em9305_dispatch_leaf_31cba4(uintptr_t record)
{
    *(volatile uint8_t *)(record+200u)=*(volatile uint8_t *)(record+290u);
}
