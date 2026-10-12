/* Native Main _thread_exit 0x4c53a6: synchronization, queue release,
 * diagnostics, and terminal CMSIS delay loop. */
#include <stdint.h>
struct ring_thread_manager {uint8_t reserved[8];void *thread;void *queue;};
extern struct ring_thread_manager audio_uart_ring_thread_manager; /* RAM 0x20004120 */
extern void audio_uart_ring_sync_exit_4c9c3c(uint32_t);
extern int32_t audio_queue_delete_peer(void *); /* selected 0x449bec */
extern void audio_delay(uint32_t); /* selected osDelay 0x449376 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="task.ring";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ring.c";
static const char fn[]="_thread_exit";
static const char deleted[]="ring message queue deleted";
static const char deleted_short[]="[task.ring]ring message queue deleted";
static const char exiting[]="thread ring exit";
static const char exiting_short[]="[task.ring]thread ring exit";
static void log_exit(uint32_t line,const char *message,const char *short_message) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,fn,line,message);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10000000u,short_message,short_message);
}
void audio_uart_ring_exit_4c53a6(void) {
    audio_uart_ring_sync_exit_4c9c3c(6u);
    if(audio_uart_ring_thread_manager.queue!=0) {
        (void)audio_queue_delete_peer(audio_uart_ring_thread_manager.queue);
        audio_uart_ring_thread_manager.queue=0;
        log_exit(362u,deleted,deleted_short);
    }
    log_exit(364u,exiting,exiting_short);
    for(;;)audio_delay(UINT32_MAX);
}
