#include <stdint.h>

/* Full native 0x32e278..0x32e2d2. EXTH/EXTB zero-extend on this ARC target;
 * SETLO/SETHS use unsigned comparisons. Volatile read order follows native. */
uint32_t opencfw_em9305_init_transition_packet_check_32e278(uintptr_t record)
{
    uint32_t lower=*(volatile uint16_t *)(record+32u);
    uint32_t upper=*(volatile uint16_t *)(record+40u);
    uint32_t preliminary=0u;
    if(lower<upper) {
        /* Native computes lower-3201 but its subsequent AND with zero makes
         * that value unobservable; other word/byte loads still execute. */
    } else {
        uint32_t sample=*(volatile uint8_t *)(record+38u);
        preliminary=(0xf384u<upper) & (sample<9u);
    }
    uint32_t high=*(volatile uint32_t *)(record+28u);
    uint32_t low=*(volatile uint32_t *)(record+24u);
    uint32_t eligible=0u;
    if((low|high)!=0u && (high&224u)==0u) {
        uint32_t middle=*(volatile uint16_t *)(record+36u);
        uint32_t adjusted=(middle-3201u)&0xffffu;
        eligible=(0xf388u<adjusted)&preliminary;
    }
    uint32_t code=*(volatile uint8_t *)(record+42u);
    uint32_t shifted=(code-17u)&0xffu;
    uint32_t is_high=shifted>=244u;
    return is_high&eligible;
}
