#include <stdint.h>

/* Native 0x3027c8..0x3027f2: 64-bit logical left shift by count & 63. */
uint64_t opencfw_em9305_child_3027c8(uint64_t value,uint32_t count)
{
    uint32_t low=(uint32_t)value,high=(uint32_t)(value>>32);
    count&=63u;
    if(count==0u)return value;
    if(count>=32u){
        high=low<<(count-32u);
        low=0u;
    }else{
        high=(high<<count)|(low>>(32u-count));
        low<<=count;
    }
    return ((uint64_t)high<<32)|low;
}
