/* Native strtoul wrapper 0x48d874 and parser 0x48d724.  The character
 * operations are the authentic locale-dependent children 0x4d58ae/c2;
 * their active locale at RAM 0x200044c0 remains a separate runtime contract. */
#include <stdint.h>
extern int32_t audio_uart_ring_locale_space_4d58ae(uint32_t);
extern int32_t audio_uart_ring_locale_lower_4d58c2(uint32_t);
extern void audio_uart_ring_errno_range_set_439cb2(void);
static int32_t digit_value(uint32_t lower) {
    if(lower>='0' && lower<='9')return (int32_t)(lower-'0');
    if(lower>='a' && lower<='z')return (int32_t)(lower-'a'+10u);
    return -1;
}
uint32_t audio_uart_ring_parse_uint_48d874(const char *text,const char **endptr,uint32_t base) {
    const char *cursor=text;
    while(audio_uart_ring_locale_space_4d58ae((uint8_t)*cursor)!=0)++cursor;
    uint32_t negative=0u;
    if(*cursor=='-' || *cursor=='+') {negative=(uint32_t)(*cursor=='-');++cursor;}
    if((int32_t)base<0 || base==1u || base>36u) {
        if(endptr)*endptr=text;
        return 0u;
    }
    const char *digit_start=cursor;
    if(base==0u) {
        if(*cursor!='0')base=10u;
        else if(((uint8_t)cursor[1]|0x20u)=='x') {base=16u;cursor+=2;digit_start=cursor;}
        else base=8u;
    } else if(base==16u && *cursor=='0' && ((uint8_t)cursor[1]|0x20u)=='x') {
        cursor+=2;digit_start=cursor;
    }
    uint32_t value=0u,overflow=0u;
    for(;;++cursor) {
        int32_t digit=digit_value((uint32_t)audio_uart_ring_locale_lower_4d58c2((uint8_t)*cursor));
        if(digit<0 || (uint32_t)digit>=base)break;
        if(value>(UINT32_MAX-(uint32_t)digit)/base)overflow=1u;
        value=value*base+(uint32_t)digit;
    }
    if(cursor==digit_start) {
        if(endptr)*endptr=text;
        return 0u;
    }
    if(overflow) {
        audio_uart_ring_errno_range_set_439cb2();
        value=UINT32_MAX;
    } else if(negative) value=0u-value;
    if(endptr)*endptr=cursor;
    return value;
}
