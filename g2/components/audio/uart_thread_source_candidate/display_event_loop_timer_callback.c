/* Native fw_event_loop_timer_callback 0x4767a8. */
#include <stdint.h>
extern void *audio_event_loop_mutex; /* RAM 0x200745f4 */
extern void *audio_event_loop_timer; /* RAM 0x200745f8 */
extern uint32_t audio_event_loop_base_tick; /* RAM 0x200745fc */
extern uint32_t audio_event_loop_elapsed; /* RAM 0x20074600 */
extern uint32_t audio_event_loop_delayed_slots[192]; /* RAM 0x2006dad4 */
extern void stock_enter_critical(void); /* selected 0x4420d0 */
extern void stock_exit_critical(void); /* selected 0x4420e8 */
extern int32_t audio_file_mutex_acquire(void *,uint32_t); /* selected 0x4497b6 */
extern int32_t audio_file_mutex_release(void *); /* selected 0x44981c */
extern void audio_event_loop_push(void (*)(void),uint32_t,uint32_t); /* native 0x4766ec */
extern int32_t audio_timer_start(void *,uint32_t); /* selected 0x449498 */
extern uint32_t g2_flashdb_candidate_tick(void); /* selected 0x4490cc */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="evtloop";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\fw_event_loop\\fw_event_loop.c";
static const char function[]="fw_evt_loop_timer_callback";
static const char lock_message[]="[fw_evt_loop_timer_callback]fw_event lock fail";
static const char lock_short[]="[evtloop][fw_evt_loop_timer_callback]fw_event lock fail";
static const char unlock_message[]="[fw_evt_loop_timer_callback]fw_event unlock fail";
static const char unlock_short[]="[evtloop][fw_evt_loop_timer_callback]fw_event unlock fail";
static const char timer_message[]="osTimerStart  next_delay %d stat = %d";
static const char timer_short[]="[evtloop]osTimerStart  next_delay %d stat = %d";
static void log_mutex(uint32_t line,const char *message,const char *short_message) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,path,function,line,message);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x04000000u,short_message,short_message);
}
void audio_event_loop_timer_callback(uint32_t marker) {
    stock_enter_critical();
    uint32_t elapsed=audio_event_loop_elapsed;
    stock_exit_critical();
    if((marker&0xff000000u)==0xff000000u) elapsed=marker&0xffffffu;
    void *mutex=audio_event_loop_mutex;
    if(audio_file_mutex_acquire(mutex,UINT32_MAX)!=0)
        log_mutex(184u,lock_message,lock_short);
    uint32_t next=UINT32_MAX;
    for(uint32_t i=0;i<64u;i++) {
        if(audio_event_loop_delayed_slots[i]!=0u) {
            uint32_t remain=audio_event_loop_delayed_slots[128u+i];
            remain=elapsed<remain?remain-elapsed:0u;
            audio_event_loop_delayed_slots[128u+i]=remain;
            if(remain==0u) {
                void (*callback)(void)=(void (*)(void))(uintptr_t)audio_event_loop_delayed_slots[i];
                audio_event_loop_delayed_slots[i]=0u;
                audio_event_loop_push(callback,audio_event_loop_delayed_slots[64u+i],1u);
            }
        }
    }
    for(uint32_t i=0;i<64u;i++) {
        if(audio_event_loop_delayed_slots[i]!=0u&&audio_event_loop_delayed_slots[128u+i]<next)
            next=audio_event_loop_delayed_slots[128u+i];
    }
    if(audio_file_mutex_release(mutex)!=0)
        log_mutex(213u,unlock_message,unlock_short);
    if(next==0x7fffffffu||next==0u) return;
    stock_enter_critical();
    audio_event_loop_elapsed=next;
    stock_exit_critical();
    int32_t status=audio_timer_start(audio_event_loop_timer,next);
    if(status!=0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,225u,timer_message,next,status);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04800000u,timer_short,timer_short,next);
    }
    audio_event_loop_base_tick=g2_flashdb_candidate_tick();
}
