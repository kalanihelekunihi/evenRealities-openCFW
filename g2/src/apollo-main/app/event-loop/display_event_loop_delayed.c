/* Native fw_event_loop_push_delayed 0x47697e and remove_delayed 0x476ace.
 * The 64-slot callback, argument, deadline arrays are contiguous RAM. */
#include <stdint.h>
extern void *audio_event_loop_thread_handle; /* RAM 0x200745f0 */
extern void *audio_event_loop_mutex; /* RAM 0x200745f4 */
extern void *audio_event_loop_timer; /* RAM 0x200745f8 */
extern uint32_t audio_event_loop_base_tick; /* RAM 0x200745fc */
extern uint32_t audio_event_loop_delayed_slots[192]; /* RAM 0x2006dad4 */
extern uint32_t audio_delay(uint32_t); /* selected osDelay 0x449376 */
extern uint32_t g2_flashdb_candidate_tick(void); /* selected 0x4490cc */
extern int32_t audio_file_mutex_acquire(void *,uint32_t); /* selected 0x4497b6 */
extern int32_t audio_file_mutex_release(void *); /* selected 0x44981c */
extern int32_t audio_timer_stop(void *); /* selected 0x4494d8 */
extern uint32_t audio_event_loop_push(void (*)(void),uint32_t,uint32_t); /* native 0x4766ec */
extern void audio_event_loop_timer_callback(uint32_t); /* native 0x4767a8 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="evtloop";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\fw_event_loop\\fw_event_loop.c";
static const char push_function[]="fw_evt_loop_push_delayed";
static const char remove_function[]="fw_evt_loop_remove_delayed";
static const char push_wait[]="[fw_evt_loop_push_delayed]wating for fw_evt_loop_thread_id init ok";
static const char push_wait_short[]="[evtloop][fw_evt_loop_push_delayed]wating for fw_evt_loop_thread_id init ok";
static const char push_lock[]="[fw_evt_loop_push_delayed]fw_event lock fail";
static const char push_lock_short[]="[evtloop][fw_evt_loop_push_delayed]fw_event lock fail";
static const char push_unlock[]="[fw_evt_loop_push_delayed]fw_event unlock fail";
static const char push_unlock_short[]="[evtloop][fw_evt_loop_push_delayed]fw_event unlock fail";
static const char remove_wait[]="fw_evt_loop_thread_id == NULL\r\n";
static const char remove_wait_short[]="[evtloop]fw_evt_loop_thread_id == NULL\r\n";
static const char remove_lock[]="[fw_evt_loop_remove_delayed]fw_event lock fail";
static const char remove_lock_short[]="[evtloop][fw_evt_loop_remove_delayed]fw_event lock fail";
static const char remove_unlock[]="[fw_evt_loop_timer_callback]fw_evt_loop_remove_delayed unlock fail";
static const char remove_unlock_short[]="[evtloop][fw_evt_loop_timer_callback]fw_evt_loop_remove_delayed unlock fail";
static void log_error(const char *function,uint32_t line,const char *message,const char *short_message) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,path,function,line,message);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x04000000u,short_message,short_message);
}
/* Stock 0x0047697E (fw_event_loop_push_delayed) */
void audio_event_loop_push_delayed(void (*callback)(void),uint32_t argument,uint32_t delay) {
    if(audio_event_loop_thread_handle==0) {
        log_error(push_function,239u,push_wait,push_wait_short);
        do {(void)audio_delay(10u);} while(audio_event_loop_thread_handle==0);
    }
    if(delay<2u) {
        (void)audio_event_loop_push(callback,argument,UINT32_MAX);
        return;
    }
    void *mutex=audio_event_loop_mutex;
    if(audio_file_mutex_acquire(mutex,UINT32_MAX)!=0)
        log_error(push_function,256u,push_lock,push_lock_short);
    uint32_t index=0u;
    while(index<64u&&audio_event_loop_delayed_slots[index]!=0u) index++;
    uint32_t elapsed=0u;
    if(index<64u) {
        audio_event_loop_delayed_slots[index]=(uint32_t)(uintptr_t)callback;
        audio_event_loop_delayed_slots[64u+index]=argument;
        elapsed=g2_flashdb_candidate_tick()-audio_event_loop_base_tick;
        audio_event_loop_delayed_slots[128u+index]=elapsed+delay;
    }
    if(audio_file_mutex_release(mutex)!=0)
        log_error(push_function,272u,push_unlock,push_unlock_short);
    if(index<64u) {
        (void)audio_timer_stop(audio_event_loop_timer);
        audio_event_loop_timer_callback(elapsed|0xff000000u);
    }
}
/* Stock 0x00476ACE (fw_event_loop_remove_delayed) */
uint32_t audio_event_loop_remove_delayed(void (*callback)(void)) {
    if(audio_event_loop_thread_handle==0) {
        log_error(remove_function,286u,remove_wait,remove_wait_short);
        return 0u;
    }
    void *mutex=audio_event_loop_mutex;
    if(audio_file_mutex_acquire(mutex,UINT32_MAX)!=0)
        log_error(remove_function,292u,remove_lock,remove_lock_short);
    uint32_t removed=0u;
    for(uint32_t i=0;i<64u;i++) {
        if(audio_event_loop_delayed_slots[i]==(uint32_t)(uintptr_t)callback) {
            audio_event_loop_delayed_slots[i]=0u;removed=1u;
        }
    }
    if(audio_file_mutex_release(mutex)!=0)
        log_error(remove_function,302u,remove_unlock,remove_unlock_short);
    if(removed!=0u) {
        uint32_t elapsed=g2_flashdb_candidate_tick()-audio_event_loop_base_tick;
        (void)audio_timer_stop(audio_event_loop_timer);
        audio_event_loop_timer_callback(elapsed|0xff000000u);
    }
    return removed;
}
