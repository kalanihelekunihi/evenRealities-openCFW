#include <stdint.h>

/* Native 0x3169b4..0x316a54: PAwR eight-slot address ring (entries of two
 * words at +0, enable byte +64, overflow flag +65, head byte +66, valid
 * mask +68). Returns 0 when disabled or the address is new (setting the
 * flag); returns 1 for a known address, which is moved to the slot before
 * the head: later valid entries shift down one slot (an empty slot ends
 * the shift and frees the vacated slot), the head steps back (7 after 0)
 * and the address is stored there as valid. */
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}

uint32_t opencfw_em9305_pawr_match_3169b4(uintptr_t ring,uint32_t low,uint32_t high)
{
    if(*(volatile uint8_t *)(ring+64u)==0u)return 0u;
    uint32_t valid=r32(ring+68u);
    uint32_t head=*(volatile uint8_t *)(ring+66u);
    uint32_t slot;
    for(slot=0u;slot<8u;++slot){
        if(((valid>>slot)&1u)==0u)continue;
        if(r32(ring+slot*8u)==low&&r32(ring+slot*8u+4u)==high)break;
    }
    if(slot==8u){
        *(volatile uint8_t *)(ring+65u)=1u;
        return 0u;
    }
    if(slot==head)return 1u;
    uint32_t to=slot;
    uint32_t from=slot==7u?0u:slot+1u;
    while(from!=head){
        if(((valid>>from)&1u)==0u){
            valid&=~(1u<<to);
            break;
        }
        uint32_t moved_high=r32(ring+from*8u+4u);
        uint32_t moved_low=r32(ring+from*8u);
        w32(ring+to*8u+4u,moved_high);
        w32(ring+to*8u,moved_low);
        to=from;
        from=from==7u?0u:from+1u;
    }
    uint32_t start=head==0u?7u:head-1u;
    *(volatile uint8_t *)(ring+66u)=(uint8_t)start;
    start&=0xffu;
    w32(ring+68u,valid|(1u<<start));
    w32(ring+start*8u+4u,high);
    w32(ring+start*8u,low);
    return 1u;
}
