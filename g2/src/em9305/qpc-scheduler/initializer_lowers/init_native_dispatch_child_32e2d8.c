#include <stdint.h>

/* Native 0x32e2d8..0x32e326: match statistics. Modes 1 and 2 compare the
 * little-endian word at key[0..3] with the expected value; mode 2 also
 * needs equal lengths, mode 1 a length of at least 4 within the limit,
 * mode 0 a zero length. Matches bump counters[0], misses counters[2];
 * other modes count nothing. */
void opencfw_em9305_dispatch_child_32e2d8(uintptr_t key, uint32_t length,
                                          uintptr_t counters, uint32_t mode,
                                          uint32_t limit, uint32_t expected)
{
    uint32_t value=0u;
    if(mode-1u<=1u){
        volatile const uint8_t *k=(volatile const uint8_t *)key;
        value=k[0]+((uint32_t)k[1]<<8)+((uint32_t)k[2]<<16)+((uint32_t)k[3]<<24);
    }
    uint32_t match;
    if(mode==2u)match=length==limit&&value==expected;
    else if(mode==1u)match=length>=4u&&limit>=length&&value==expected;
    else if(mode==0u)match=length==0u;
    else return;
    volatile uint32_t *counter=(volatile uint32_t *)(counters+(match?0u:8u));
    *counter=*counter+1u;
}
