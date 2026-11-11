#include <stdint.h>

/* Native 0x317418..0x317496: advance a nested event counter. The config
 * gives per-slot ticks (+24), slots per round (+27), a final-round flag
 * (+26), a threshold (+25) and a round limit (+52); the state bytes are
 * {round, slot, sub-round, overflow, tick}. Returns 0 only when the
 * round counter reaches the limit, 1 otherwise. */
uint32_t opencfw_em9305_dispatch_child_317418(uintptr_t config, uintptr_t state)
{
    volatile const uint8_t *c=(volatile const uint8_t *)config;
    volatile uint8_t *s=(volatile uint8_t *)state;
    uint32_t per_slot=c[24];
    uint32_t slots=c[27];
    uint32_t next=s[4]+1u;
    uint32_t tick=(uint8_t)next;
    uint32_t round,limit;
    s[4]=(uint8_t)next;
    if(tick<per_slot*slots){
        next=s[1]+1u;
        s[1]=(uint8_t)next;
        if((uint8_t)next<per_slot)return 1u;
        next=s[2]+1u;
        s[1]=0u;
        s[2]=(uint8_t)next;
        if((int32_t)(uint8_t)next<(int32_t)(slots-1u))return 1u;
        uint32_t final=c[26];
        s[2]=0u;
        if(final!=0u)return 1u;
        if(tick<c[25])return 1u;
        round=s[0];
        limit=c[52];
        s[4]=0u;
    }else{
        uint32_t overflow=s[3];
        uint32_t threshold=c[25];
        s[1]=(uint8_t)(per_slot-1u);
        s[3]=(uint8_t)(overflow+1u);
        if(tick<threshold)return 1u;
        round=s[0];
        limit=c[52];
        s[4]=0u;
        s[3]=0u;
        s[1]=0u;
    }
    s[0]=(uint8_t)(round+1u);
    return (uint8_t)(round+1u)<limit;
}
