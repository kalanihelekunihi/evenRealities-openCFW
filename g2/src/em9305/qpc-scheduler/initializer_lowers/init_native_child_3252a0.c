#include <stdint.h>

/* Native 0x3252a0..0x3252b8: average of four signed RSSI samples; the sum
 * is shifted logically by two and the low byte sign-extended. */
int32_t opencfw_em9305_child_3252a0(uintptr_t samples)
{
    volatile const int8_t *s=(volatile const int8_t *)samples;
    uint32_t sum=0u;
    for(uint32_t index=0u;index<4u;++index)sum+=(uint32_t)(int32_t)s[index];
    return (int8_t)(sum>>2);
}
