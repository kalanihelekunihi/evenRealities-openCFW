/* Native thread-manager system-start synchronization 0x4c9b86/0x4c9be2. */
#include <stdint.h>
extern uint32_t audio_flags_wait(uint32_t,uint32_t,uint32_t); /* selected 0x4492c2 */
extern uint32_t g2_log_event_set_task(uint32_t,uint32_t); /* selected 0x4495e4 */
extern uint8_t audio_uart_thread_manager_state[]; /* live RAM 0x200040d8 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="task.manager";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_manager.c";
static const char start_fn[]="thread_manager_sysstart_sync";
static const char end_fn[]="thread_manager_sysstart_sync_end";
static const char start_fmt[]="thread %d sync start:";
static const char end_fmt[]="thread %d sync end";
static const char start_short[]="[task.manager]thread %d sync start:";
static const char end_short[]="[task.manager]thread %d sync end";
uint32_t audio_uart_ring_state_transition_4c9b86(uint32_t index) {
    while((audio_flags_wait(0x800000u,1u,UINT32_MAX)&0x800000u)==0u){}
    uint32_t result=index;
    if((audio_log_flags()&2u)!=0u) {
        audio_log_extended(3u,module,path,start_fn,433u,start_fmt,(uint8_t)index);
        result=433u;
    }
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c400000u,start_short,start_short,(uint8_t)index);
    return result;
}
uint32_t audio_uart_ring_resource_transition_4c9be2(uint32_t index) {
    uint32_t result=index;
    if((audio_log_flags()&2u)!=0u) {
        audio_log_extended(3u,module,path,end_fn,447u,end_fmt,(uint8_t)index);
        result=447u;
    }
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c400000u,end_short,end_short,(uint8_t)index);
    uint32_t handle=*(uint32_t *)(void *)(audio_uart_thread_manager_state+0x1cu);
    uint32_t shift=index&0xffu;
    uint32_t mask=shift<32u?1u<<shift:0u;
    (void)g2_log_event_set_task(handle,mask);
    return result;
}
void audio_uart_ring_sync_exit_4c9c3c(uint32_t index) {
    uint32_t handle=*(uint32_t *)(void *)(audio_uart_thread_manager_state+0x1cu);
    uint32_t shift=index&0xffu;
    uint32_t mask=shift<32u?1u<<shift:0u;
    (void)g2_log_event_set_task(handle,mask);
}
