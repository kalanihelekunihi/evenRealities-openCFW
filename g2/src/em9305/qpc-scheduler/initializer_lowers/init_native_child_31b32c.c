#include <stdint.h>

/* Native 0x31b32c..0x31b374: compare the midpoint of the two signed
 * bytes +2/+3 with the target and return a clamped step in -2..4, or 0
 * when the step is positive and not allowed (flag bit 0 clear) or
 * negative and not forced (force bit 0 clear). */
int32_t opencfw_em9305_child_31b32c(uintptr_t range,int32_t target,
                                    uint32_t allow_up,uint32_t force)
{
    int32_t low=*(volatile int8_t *)(range+2u);
    int32_t high=*(volatile int8_t *)(range+3u);
    int32_t middle=(int8_t)((high-low)/2+low);
    int32_t delta=middle-target;
    if(delta>0&&(allow_up&1u)==0u)return 0;
    if(delta<0&&(force&1u)==0u)return 0;
    if(delta>=5)return 4;
    if(delta>-3)return (int8_t)delta;
    return -2;
}
