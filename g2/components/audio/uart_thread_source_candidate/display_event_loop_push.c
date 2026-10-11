/* Native fw_event_loop_push 0x4766ec. */
#include <stdint.h>
extern void *audio_event_loop_thread_handle; /* RAM 0x200745f0 */
extern void *audio_event_loop_queue; /* RAM 0x200745ec */
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t); /* selected 0x449abe */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="evtloop";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\fw_event_loop\\fw_event_loop.c";
static const char function[]="fw_evt_loop_push";
static const char no_thread[]="[fw_evt_loop_push]fw_evt_loop_thread_id is NULL";
static const char no_thread_short[]="[evtloop][fw_evt_loop_push]fw_evt_loop_thread_id is NULL";
static const char put_error[]="[fw_evt_loop_push]fw_event_push error:0x%x";
static const char put_error_short[]="[evtloop][fw_evt_loop_push]fw_event_push error:0x%x";
void audio_event_loop_push(void (*callback)(void),uint32_t argument,uint32_t timeout) {
    if(audio_event_loop_thread_handle==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,150u,no_thread);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,no_thread_short,no_thread_short);
        return;
    }
    if(audio_event_loop_queue!=0) {
        struct event_message {uint32_t argument;uint32_t callback;} message;
        message.argument=argument;message.callback=(uint32_t)(uintptr_t)callback;
        int32_t status=audio_cmsis_queue_put(audio_event_loop_queue,&message,0u,timeout);
        if(status!=0) {
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(1u,module,path,function,160u,put_error,status);
            if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x04400000u,put_error_short,put_error_short,status);
        }
    }
}
