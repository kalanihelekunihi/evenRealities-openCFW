/* Stock 0x44a108..0x44a191: RTC calendar record to seconds. */
#include <stdint.h>
static uint32_t get_word(const uint8_t *p)
{
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
uint32_t audio_time_epoch_seconds(const uint8_t in[40])
{
    uint32_t y=(get_word(in+12u)+2000u)%100u;
    uint32_t month=get_word(in+16u);
    uint32_t adjust=month<3u?0u:((y&3u)==0u?1u:2u);
    uint32_t days=10957u+365u*(uint16_t)y+((uint16_t)(y+3u))/4u;
    days+=((367u*month-362u)/12u)-adjust;
    days+=get_word(in+20u)-1u;
    uint32_t seconds=days*86400u;
    seconds+=get_word(in+24u)*3600u;
    seconds+=get_word(in+28u)*60u;
    seconds+=get_word(in+32u);
    if(get_word(in+36u)>=50u) seconds++;
    return seconds;
}
