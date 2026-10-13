#include <stdint.h>
extern void audio_uart_nema_error_set_4b127c(uint32_t);
extern void audio_uart_nema_list_finalize_514b7c(void *);
extern void audio_uart_nema_submit_523f10(uint32_t);
extern int32_t audio_uart_nema_poll_514026(uint32_t);
static int32_t rollover_divide(int32_t a,int32_t b) {
    if(b==0)return 0;
    if(a==INT32_MIN && b==-1)return INT32_MIN;
    return a/b;
}
/* Native5147b0..514846: preserve native quarter-sector policy and ready1 unconditional submit. */
void audio_uart_nema_sector_rollover_5147b0(void *cell) {
    volatile uint32_t *list=(volatile uint32_t *)cell;
    if(!list) {audio_uart_nema_error_set_4b127c(8192u);return;}
    uint32_t flags=((volatile uint8_t *)cell)[24];
    uint32_t used=list[5];
    if(flags&32u) {
        uint32_t sector=list[11];
        int32_t quotient=rollover_divide((int32_t)used,(int32_t)sector);
        if(used-sector*(uint32_t)quotient==0u)return;
    } else if(used==0u)return;
    audio_uart_nema_list_finalize_514b7c(cell);
    if(((volatile uint8_t *)cell)[24]&32u) {
        volatile uint8_t *context=*(volatile uint8_t * volatile *)(uintptr_t)0x20074efcu;
        uint32_t ready=context[249];
        if(ready!=1u) {
            uint32_t capacity=list[10],quarter=capacity>>2,position=list[12];
            if(position!=quarter && position!=(capacity>>1) && position!=quarter*3u && position!=0u && list[13]!=0x00ffffffu)goto after_submit;
        }
        audio_uart_nema_submit_523f10(list[13]);
        list[7]=list[13];
    } else audio_uart_nema_submit_523f10(list[7]);
after_submit:
    if(list[7]==0x00ffffffu && audio_uart_nema_poll_514026(0x00ffffffu)>=0)list[7]=UINT32_MAX;
}
