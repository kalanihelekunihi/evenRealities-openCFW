/* Native Main thread_ring_entry 0x4c4cec and adjacent startup wrappers. */
#include <stdint.h>
extern void thread_ring_queue_init(void);
extern void audio_uart_ring_state_transition_4c9b86(uint32_t);
extern void audio_uart_ring_resource_transition_4c9be2(uint32_t);
extern uint32_t audio_flags_wait(uint32_t,uint32_t,uint32_t); /* selected 0x4492c2 */
extern uint32_t audio_uart_ring_notify_event_4c507e(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="task.ring";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ring.c";
static const char function[]="thread_ring";
static const char error[]="Notify error!";
static const char short_error[]="[task.ring]Notify error!";
void thread_ring_state_enter(void) {audio_uart_ring_state_transition_4c9b86(6u);}
void thread_ring_resource_hook(void) {} /* authenticated 0x4c4d8e bx lr */
void thread_ring_state_ready(void) {audio_uart_ring_resource_transition_4c9be2(6u);}
void thread_ring_init_hook(void) {} /* authenticated 0x4c4d64 bx lr */
void thread_ring_entry(void *unused) {
    (void)unused;
    thread_ring_state_enter();
    thread_ring_queue_init();
    thread_ring_init_hook();
    thread_ring_resource_hook();
    thread_ring_state_ready();
    for(;;) {
        uint32_t bits;
        while((bits=audio_flags_wait(0x00ffffffu,0u,UINT32_MAX))!=0u &&
              bits<0x80000000u)
            (void)audio_uart_ring_notify_event_4c507e(bits);
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,100u,error);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,short_error,short_error);
    }
}
