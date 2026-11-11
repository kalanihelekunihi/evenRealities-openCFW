#include <stdint.h>

/* Native 0x312be4..0x312c5a: air time of a payload split into fragments.
 * Fragment overhead/limit come from the fixed-size flag (66/66) or the
 * chunk size (chunk/chunk, or 10/5 when 0); a zero fragment size means
 * 257 minus overhead. A payload within one fragment costs one piece;
 * otherwise full fragments (count from the quotient, one fewer when the
 * remainder's low halfword is 0) each cost piece + gap + 300 us, plus a
 * piece for the remainder. The stock multiplies are 16-bit (signed for
 * the remainder, unsigned for the fragment count). Callers keep the
 * divisor nonzero (chunk is never 257). */
extern uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t,uint32_t,uint32_t);

uint32_t opencfw_em9305_radio_duration_312be4(uint32_t phy,uint32_t fragment,uint32_t base,
                                              uint32_t gap,uint32_t length,uint32_t fixed,
                                              uint32_t mode,uint32_t chunk)
{
    uint32_t overhead=66u,tail=66u;
    if(fixed==0u) {
        if(chunk!=0u) {
            overhead=chunk;
            tail=chunk;
        } else {
            overhead=10u;
            tail=5u;
        }
    }
    uint32_t step=fragment,limit=fragment;
    if(fragment==0u) {
        step=257u-overhead;
        limit=257u-tail;
    }
    uint32_t total;
    if(limit>=length) {
        total=opencfw_em9305_radio_duration_piece_312b88(phy,mode,(uint16_t)(tail+length));
    } else {
        uint32_t count=length/step;
        uint32_t rest=length-(uint32_t)((int32_t)(int16_t)count*(int16_t)step);
        if((uint16_t)rest==0u) count-=1u;
        uint32_t piece=opencfw_em9305_radio_duration_piece_312b88(phy,mode,overhead+step);
        total=(piece+gap+300u)*(count&0xffffu);
        if((uint16_t)rest!=0u)
            total+=opencfw_em9305_radio_duration_piece_312b88(phy,mode,(uint16_t)(rest+tail));
    }
    return total+base;
}
