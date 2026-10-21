/* LVGL lv_timer_handler native 0x464344. List/clock children are authentic
 * native code contracts; product LVGL scheduler state is RAM0x2006f548. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_state[]; /* RAM0x2006f548, at least 0x9c */
extern void audio_uart_lv_lock(void); /* 0x49acba */
extern void audio_uart_lv_unlock(void); /* 0x49acc4 */
extern uint32_t audio_uart_lv_tick(void); /* 0x473482 */
extern uint32_t audio_uart_lv_elapsed(uint32_t); /* 0x4734a0 */
extern void *audio_uart_lv_list_first(void *); /* 0x482cd8 */
extern void *audio_uart_lv_list_next(void *,void *); /* 0x482cf0 */
extern uint32_t audio_uart_lv_timer_execute(void *); /* 0x464604 */
extern uint32_t audio_uart_lv_timer_remaining(void *); /* 0x46467c */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                               const char *,const char *); /* native 0x44d25c */
static uint32_t get32(uint8_t *p,uint32_t o) {
    return *(uint32_t *)(void *)(p+o);
}
static void set32(uint8_t *p,uint32_t o,uint32_t v) {
    *(uint32_t *)(void *)(p+o)=v;
}
uint32_t audio_uart_display_process(void) {
    uint8_t *s=audio_uart_display_lv_state;
    if(s[0x88u]!=0u) return 1u;
    s[0x88u]=1u;
    if(s[0x80u]==0u) {s[0x88u]=0u;return 1u;}
    audio_uart_lv_lock();
    uint32_t start=audio_uart_lv_tick();
    if(start==0u) {
        uint32_t n=get32(s,0x98u)+1u;
        set32(s,0x98u,n);
        if(n>100u) {
            set32(s,0x98u,0u);
            static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_timer.c";
            static const char fn[]="lv_timer_handler";
            static const char message[]="It seems lv_tick_inc() is not called.";
            audio_uart_lvgl_log(2u,source,0x59u,fn,message);
        }
    }
    uint32_t restart;
    do {
        restart=0u;
        s[0x82u]=0u;s[0x83u]=0u;
        void *list=s+0x74u;
        for(void *timer=audio_uart_lv_list_first(list);timer!=0;
            timer=audio_uart_lv_list_next(list,timer)) {
            if(audio_uart_lv_timer_execute(timer)!=0u &&
               (s[0x83u]!=0u||s[0x82u]!=0u)) {restart=1u;break;}
        }
    } while(restart!=0u);
    uint32_t minimum=UINT32_MAX;
    void *list=s+0x74u;
    for(void *timer=audio_uart_lv_list_first(list);timer!=0;
        timer=audio_uart_lv_list_next(list,timer)) {
        if((*(const uint8_t *)(const void *)((const uint8_t *)timer+0x14u)&1u)==0u) {
            uint32_t remaining=audio_uart_lv_timer_remaining(timer);
            if(remaining<minimum) minimum=remaining;
        }
    }
    set32(s,0x90u,get32(s,0x90u)+audio_uart_lv_elapsed(start));
    uint32_t duration=audio_uart_lv_elapsed(get32(s,0x94u));
    if(duration>499u) {
        uint8_t utilization=(uint8_t)(get32(s,0x90u)*100u/duration);
        s[0x81u]=(uint8_t)(utilization<101u?100u-utilization:0u);
        set32(s,0x90u,0u);
        set32(s,0x94u,audio_uart_lv_tick());
    }
    set32(s,0x84u,minimum);
    s[0x88u]=0u;
    audio_uart_lv_unlock();
    return minimum;
}
