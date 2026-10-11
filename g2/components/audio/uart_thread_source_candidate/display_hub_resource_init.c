/* Native HUB_ResourceInit 0x4a66ee: queue and one-shot timer construction. */
#include <stdint.h>
struct timer_attributes {const char *name;uint32_t flags;void *control_block;uint32_t control_block_size;};
extern void *audio_hub_send_queue; /* live RAM 0x20003670 */
extern void *audio_hub_timer_handle; /* live RAM 0x20074908 */
extern uint8_t audio_hub_timer_control_block[44]; /* source-owned storage, RAM 0x20073650 */
extern void audio_hub_timer_callback(void *); /* native 0x4a696c */
extern void *audio_queue_new(uint32_t,uint32_t,const void *); /* selected 0x449a32 */
extern void *audio_uart_timer_new(void (*)(void *),uint32_t,void *,const void *); /* native 0x4493b0 */
extern uint32_t audio_log_flags(void); /* selected 0x43d0ce */
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...); /* selected 0x43d574 */
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...); /* selected 0x43ce9e */
static const char module[]="sensor_hub";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\sensor_hub\\sensor_hub.c";
static const char function[]="HUB_ResourceInit";
static const char q_failed[]="[HUB_ResourceInit]osMessageQueueNew fail";
static const char q_failed_short[]="[sensor_hub][HUB_ResourceInit]osMessageQueueNew fail";
static const char q_success[]="[HUB_ResourceInit]osMessageQueueNew:0x%x, success";
static const char q_success_short[]="[sensor_hub][HUB_ResourceInit]osMessageQueueNew:0x%x, success";
static const char t_failed[]="[HUB_ResourceInit]osTimerNew failed";
static const char t_failed_short[]="[sensor_hub][HUB_ResourceInit]osTimerNew failed";
static const char t_success[]="[HUB_ResourceInit]osTimerNew success";
static const char t_success_short[]="[sensor_hub][HUB_ResourceInit]osTimerNew success";
static const char timer_name[]="sensor_hub_timer";
static const struct timer_attributes timer_attrs={timer_name,0u,
                                                  audio_hub_timer_control_block,44u};
static void log_queue(void *queue) {
    if(queue==0) {
        if(audio_log_flags()&2u)
            audio_log_extended(1u,module,path,function,99u,q_failed);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x04000000u,q_failed_short,q_failed_short);
    } else {
        if(audio_log_flags()&2u)
            audio_log_extended(4u,module,path,function,101u,q_success,queue);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x10400000u,q_success_short,q_success_short,queue);
    }
}
static void log_timer(void *timer) {
    if(timer==0) {
        if(audio_log_flags()&2u)
            audio_log_extended(1u,module,path,function,107u,t_failed);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x04000000u,t_failed_short,t_failed_short);
    } else {
        if(audio_log_flags()&2u)
            audio_log_extended(4u,module,path,function,109u,t_success);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x10000000u,t_success_short,t_success_short);
    }
}
void audio_hub_resource_init(void) {
    audio_hub_send_queue=audio_queue_new(50u,8u,0);
    log_queue(audio_hub_send_queue);
    if(audio_hub_timer_handle==0) {
        audio_hub_timer_handle=audio_uart_timer_new(audio_hub_timer_callback,
                                                    1u,0,&timer_attrs);
        log_timer(audio_hub_timer_handle);
    }
}
