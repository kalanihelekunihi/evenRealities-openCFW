/* Native ALS curve chain 0x4add02/24/30/3c/6a/8c and ROM table 0x730e24. */
#include <stdint.h>
struct als_step {uint32_t threshold;uint32_t percent;};
static const struct als_step curve[6]={
    {10u,35u},{200u,50u},{400u,70u},{1000u,70u},{1300u,100u},{0xffffffffu,100u}
};
extern uint32_t audio_als_scale_active; /* RAM 0x20000064 */
extern uint32_t audio_als_curve_index; /* RAM 0x200741e4 */
extern uint32_t audio_als_curve_nominal; /* RAM 0x200741e8 */
extern uint32_t audio_als_curve_adjusted; /* RAM 0x200741ec */
static uint32_t curve_index(uint32_t input) {
    for(uint32_t i=0;i<6u;i++) if(input<=curve[i].threshold) return i;
    return 5u;
}
static uint32_t curve_percent(uint32_t index) {return curve[index].percent;}
static uint32_t curve_adjust(uint32_t percent,uint32_t scale) {
    if(percent<=35u) return 35u;
    uint64_t product=(uint64_t)(percent-35u)*scale+512u;
    uint32_t value=35u+(uint32_t)(product>>10);
    return value>100u?100u:value;
}
void audio_als_apply_previous(uint32_t prior) {
    uint32_t index=curve_index(prior);
    audio_als_curve_index=index;
    audio_als_curve_nominal=curve_percent(curve_index(prior));
    uint32_t percent=curve_percent(index);
    audio_als_curve_adjusted=index+1u<6u ? curve_adjust(percent,audio_als_scale_active):100u;
}
