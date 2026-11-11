#include <stdint.h>

/* Native 0x3027f4..0x302816: 64-bit logical shift right, count taken
 * modulo 64 (libgcc __lshrdi3 shape, without the libgcc call). */
uint64_t opencfw_em9305_child_3027f4(uint64_t value, uint32_t count)
{
    uint32_t low=(uint32_t)value,high=(uint32_t)(value>>32);
    count&=63u;
    if(count==0u)return value;
    if(count>=32u){
        low=high>>(count-32u);
        high=0u;
    }else{
        low=(low>>count)|(high<<(32u-count));
        high>>=count;
    }
    return ((uint64_t)high<<32)|low;
}
