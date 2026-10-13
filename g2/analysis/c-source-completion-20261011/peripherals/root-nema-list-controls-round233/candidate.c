#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern void audio_uart_nema_error_set_4b127c(uint32_t);
extern void audio_uart_nema_sector_rollover_5147b0(void *);
extern int32_t audio_uart_nema_poll_514026(uint32_t);
/* Native514384..5143d4: parent redirection, chained rewind and bound-parent update. */
void audio_uart_nema_cl_rewind_514384(void *cell) {
    volatile uint32_t *list=cell;
    if(!list) {audio_uart_nema_error_set_4b127c(8192u);return;}
    uint32_t parent=list[9];
    if(parent)list=(volatile uint32_t *)(uintptr_t)parent;
    do {
        parent=list[9];
        if(parent) {
            volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)*(volatile uint32_t *)audio_uart_nema_context_cell;
            if(context[1]==(uint32_t)(uintptr_t)list)context[1]=parent;
        }
        list[5]=0;list[12]=0;
        list[6]=list[6]&~4u;
        list=(volatile uint32_t *)(uintptr_t)list[8];
    }while(list);
}
/* Native514cf2..514d00: context byte precedes the tail-called rollover. */
void audio_uart_nema_cl_submit_514cf2(void *cell) {
    volatile uint8_t *context=(volatile uint8_t *)(uintptr_t)*(volatile uint32_t *)audio_uart_nema_context_cell;
    context[249]=1;
    audio_uart_nema_sector_rollover_5147b0(cell);
}
/* Native514d00..514d2c: negative ID skips polling; successful poll resets ID. */
int32_t audio_uart_nema_cl_wait_514d00(void *cell) {
    volatile uint32_t *list=cell;
    if(!list){audio_uart_nema_error_set_4b127c(8192u);return -1;}
    uint32_t submission=list[7];
    if((int32_t)submission<0 || audio_uart_nema_poll_514026(submission)>=0)list[7]=UINT32_MAX;
    return 0;
}
