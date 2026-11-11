#include <stdint.h>

/* Native 0x316a68..0x316a8c: store the first word and a packed field word
 * (bits 0..8 low, 9..10 kind, 11..15 a, 16..19 b, 20.. top). */
void opencfw_em9305_child_316a68(uintptr_t out,uint32_t kind,uint32_t first,
                                 uint32_t low,uint32_t a,uint32_t b,
                                 uint32_t top)
{
    *(volatile uint32_t *)out=first;
    uint32_t packed=((kind&3u)<<9)+(low&0x1ffu)+((a&0x1fu)<<11)
                   +((b&0xfu)<<16)+(top<<20);
    *(volatile uint32_t *)(out+4u)=packed;
}
