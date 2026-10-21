/* Native ring_task_msg_send 0x4c549c. Its message ownership transfers to
 * the queue on successful put and is released on failure. */
#include <stdint.h>
struct ring_thread_manager {uint8_t reserved[8];void *thread;void *queue;};
extern struct ring_thread_manager audio_uart_ring_thread_manager; /* 0x20004120 */
extern void *file_heap_allocate(uint32_t); /* native 0x474cd2 allocator contract */
extern void audio_file_heap_free(void *); /* selected 0x474d16 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t); /* selected 0x449abe */
extern uint32_t audio_thread_flags_set(void *,uint32_t); /* selected 0x449238 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="task.ring";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ring.c";
static const char function[]="Thread_SendMsgToRingTaskWithId";
static const char null_data[]="msg ring pdata is null";
static const char null_data_short[]="[task.ring]msg ring pdata is null";
static const char no_queue[]="g_thread_ring queue";
static const char no_queue_short[]="[task.ring]g_thread_ring queue";
static const char no_memory[]="ring_task_msg_send alloc fail";
static const char no_memory_short[]="[task.ring]ring_task_msg_send alloc fail";
static const char put_failed[]="msg dispatch send msg miss";
static const char put_failed_short[]="[task.ring]msg dispatch send msg miss";
static void log_error(uint32_t line,const char *message,const char *compact) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,path,function,line,message);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x04000000u,compact,compact);
}
int32_t audio_uart_ring_task_msg_send(uint32_t id,const void *data,uint32_t length) {
    uint32_t size=(uint16_t)length;
    if(data==0 && size!=0u) {
        log_error(0x182u,null_data,null_data_short);
        return -1;
    }
    if(audio_uart_ring_thread_manager.queue==0) {
        log_error(0x187u,no_queue,no_queue_short);
        return -1;
    }
    uint8_t *node=(uint8_t *)file_heap_allocate(size+8u);
    if(node==0) {
        log_error(399u,no_memory,no_memory_short);
        return -1;
    }
    audio_uart_buffer_zero(node,8u,0u);
    *(uint32_t *)(void *)node=id;
    *(uint32_t *)(void *)(node+4u)=size;
    if(size!=0u && data!=0)
        (void)audio_queue_copy_bytes(node+8u,data,size);
    if(audio_cmsis_queue_put(audio_uart_ring_thread_manager.queue,&node,0u,0u)==0) {
        (void)audio_thread_flags_set(audio_uart_ring_thread_manager.thread,0x400000u);
        return 0;
    }
    log_error(0x19cu,put_failed,put_failed_short);
    audio_file_heap_free(node);
    return -1;
}
