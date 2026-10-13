#include <stdint.h>
extern int32_t audio_uart_ambiq_color_format_src_4b05a4(uint32_t);
/* Native4c7548..4c76a8: return0 on all paths; acceptance changes two bytes. */
int32_t audio_uart_ambiq_evaluate_4c7548(void *unit,void *task) {
    (void)unit;
    volatile uint8_t *t=task;
    switch(t[4]) {
    case 1: {
        volatile uint8_t *d=(void *)(uintptr_t)*(volatile uint32_t *)(t+84u);
        if((d[47]&15u)==4u||(d[47]&15u)==5u||(d[47]&15u)==3u)return 0;
        break;
    }
    case 10: {
        volatile uint8_t *d=(void *)(uintptr_t)*(volatile uint32_t *)(t+84u);
        if((d[67]&15u)==4u||(d[67]&15u)==5u||(d[67]&15u)==3u)return 0;
        break;
    }
    case 6: {
        volatile uint8_t *d=(void *)(uintptr_t)*(volatile uint32_t *)(t+84u);
        uint32_t cf=(uint8_t)(*(volatile uint32_t *)(d+32u)>>8);
        if(audio_uart_ambiq_color_format_src_4b05a4(cf)==-1)return 0;
        if((d[81]&7u)==2u||(d[81]&7u)==3u)return 0;
        break;
    }
    case 2:case 3:case 5:case 7:case 8:case 9:case 11:case 13:break;
    default:return 0;
    }
    t[89]=10u;
    t[88]=9u;
    return 0;
}
