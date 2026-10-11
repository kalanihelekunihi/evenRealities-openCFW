/* Native fw_event_loop_initialize 0x4764e0 and worker 0x476680. */
#include <stdint.h>
struct queue_attrs {const char *name;uint32_t bits;void *cb;uint32_t cb_size;void *storage;uint32_t storage_size;};
struct timer_attrs {const char *name;uint32_t bits;void *cb;uint32_t cb_size;};
struct thread_attrs {const char *name;uint32_t bits;void *cb;uint32_t cb_size;void *stack;uint32_t stack_size;uint32_t priority;uint32_t tz;uint32_t reserved;};
extern void *audio_event_loop_queue; /* RAM 0x200745ec */
extern void *audio_event_loop_timer; /* RAM 0x200745f8 */
extern void *audio_event_loop_mutex; /* RAM 0x200745f4 */
extern void *audio_event_loop_thread_handle; /* RAM 0x200745f0 */
extern uint8_t audio_event_loop_queue_cb[80]; /* RAM 0x20072b28 */
extern uint8_t audio_event_loop_queue_storage[120]; /* RAM 0x20071d40 */
extern uint8_t audio_event_loop_timer_cb[44]; /* RAM 0x20073624 */
extern uint8_t audio_event_loop_mutex_cb[80]; /* RAM 0x20072b78 */
extern uint8_t audio_event_loop_thread_cb[112]; /* RAM 0x20071f80 */
extern uint8_t audio_event_loop_thread_stack[3072]; /* RAM 0x20372bc0 */
extern void *audio_queue_new(uint32_t,uint32_t,const void *); /* selected 0x449a32 */
extern void *audio_uart_timer_new(void (*)(void *),uint32_t,void *,const void *); /* selected 0x4493b0 */
extern void *audio_uart_mutex_new(const void *); /* selected 0x44971c */
extern int32_t audio_thread_terminate_peer(void *); /* selected 0x4491fe */
extern void *audio_thread_new(void (*)(void *),void *,const void *); /* selected 0x4490e2 */
extern int32_t audio_uart_queue_receive(void *,void *,uint32_t,uint32_t); /* CMSIS osMessageQueueGet 0x449b3c, complete selected C body */
extern void audio_event_loop_timer_callback(uint32_t); /* native 0x4767a8 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="evtloop";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\fw_event_loop\\fw_event_loop.c";
static const char init_function[]="fw_evt_loop_init";
static const char task_function[]="fw_evt_loop_task";
static const char queue_name[]="fw_evt_loop_mesq"; /* ROM 0x77f630 */
static const char timer_mutex_name[]="fw_evt_loop_mutex"; /* ROM 0x77f644 */
static const char thread_name[]="evt_loop"; /* ROM 0x78aacc */
static const char queue_error[]="[fw_evt_loop_init]osMessageQueueNew, fail";
static const char queue_error_short[]="[evtloop][fw_evt_loop_init]osMessageQueueNew, fail";
static const char timer_error[]="[fw_evt_loop_init]osTimerNew, failed";
static const char timer_error_short[]="[evtloop][fw_evt_loop_init]osTimerNew, failed";
static const char mutex_error[]="Warning: failed to Create fw_evt_loop_mutex_id";
static const char mutex_error_short[]="[evtloop]Warning: failed to Create fw_evt_loop_mutex_id";
static const char thread_error[]="[fw_evt_loop_init]osThreadNew, fail";
static const char thread_error_short[]="[evtloop][fw_evt_loop_init]osThreadNew, fail";
static const char task_error[]="[fw_evt_loop_task]app treat event invalid status:%d";
static const char task_error_short[]="[evtloop][fw_evt_loop_task]app treat event invalid status:%d";
static void log_init(uint32_t line,const char *message,const char *short_message) {
    if((audio_log_flags()&2u)!=0u)audio_log_extended(1u,module,path,init_function,line,message);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x04000000u,short_message,short_message);
}
static void timer_bridge(void *argument) {
    audio_event_loop_timer_callback((uint32_t)(uintptr_t)argument);
}
void audio_event_loop_task(void *unused) {
    (void)unused;
    for(;;) {
        struct event_message {uint32_t argument;void (*callback)(uint32_t);} message;
        int32_t status=audio_uart_queue_receive(audio_event_loop_queue,&message,0u,UINT32_MAX);
        if(status==0) {message.callback(message.argument);continue;}
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,task_function,140u,task_error,status);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04400000u,task_error_short,task_error_short,status);
    }
}
void audio_event_loop_initialize(void) {
    if(audio_event_loop_queue==0) {
        const struct queue_attrs attr={queue_name,0u,audio_event_loop_queue_cb,80u,
                                       audio_event_loop_queue_storage,120u};
        audio_event_loop_queue=audio_queue_new(15u,8u,&attr);
        if(audio_event_loop_queue==0)log_init(88u,queue_error,queue_error_short);
    }
    if(audio_event_loop_timer==0) {
        const struct timer_attrs attr={timer_mutex_name,0u,audio_event_loop_timer_cb,44u};
        audio_event_loop_timer=audio_uart_timer_new(timer_bridge,0u,0,&attr);
        if(audio_event_loop_timer==0)log_init(97u,timer_error,timer_error_short);
    }
    if(audio_event_loop_mutex==0) {
        const struct timer_attrs attr={timer_mutex_name,0u,audio_event_loop_mutex_cb,80u};
        audio_event_loop_mutex=audio_uart_mutex_new(&attr);
        if(audio_event_loop_mutex==0)log_init(106u,mutex_error,mutex_error_short);
    }
    if(audio_event_loop_thread_handle!=0) {
        (void)audio_thread_terminate_peer(audio_event_loop_thread_handle);
        audio_event_loop_thread_handle=0;
    }
    if(audio_event_loop_thread_handle==0) {
        const struct thread_attrs attr={thread_name,0u,audio_event_loop_thread_cb,112u,
                                        audio_event_loop_thread_stack,3072u,38u,0u,0u};
        audio_event_loop_thread_handle=audio_thread_new(audio_event_loop_task,0,&attr);
        if(audio_event_loop_thread_handle==0)log_init(121u,thread_error,thread_error_short);
    }
}
