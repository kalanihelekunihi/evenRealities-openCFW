/* Apollo CommonEventDataPacket 0x464772. The second queue is RAM 0x200749d0. */
#include <stdint.h>

extern void *g2_uart_send_queue;                 /* RAM 0x200749cc */
extern void *audio_uart_master_schedule_queue;  /* RAM 0x200749d0 */
extern void *g2_uart_thread_event;               /* RAM 0x20074b10 */
extern void *audio_uart_alloc_retry(uint32_t);
extern void audio_file_heap_free(void *);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern uint8_t audio_uart_device_role_get(void);
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t);
extern uint32_t osEventFlagsSet(void *,uint32_t);
extern void audio_delay_scheduler_assert(void);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="sync.module.api";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_interface_api.c";
static const char function[]="CommonEventDataPacket";
#define LOG(level,line,mask,plain,compact,...) do { \
    uint32_t flags=audio_log_level(); \
    if((flags&2u)!=0u) \
        audio_log_extended(level,module,path,function,line,plain,##__VA_ARGS__); \
    flags=audio_log_level(); \
    if((flags&1u)!=0u || (audio_log_level()&4u)!=0u) \
        (void)compressed_log_output(mask,compact,compact,##__VA_ARGS__); \
} while(0)

int32_t audio_uart_master_request_core_464772(uint32_t id,const void *payload,
                                                uint32_t length,uint32_t context,
                                                uint32_t kind,uint32_t target,
                                                uint32_t channel)
{
    uint16_t bytes=(uint16_t)length;
    if(g2_uart_send_queue==0) {
        LOG(1u,0x2bu,0x04000000u,"uart send queue is NULL !!!",
            "[sync.module.api]uart send queue is NULL !!!");
        return -1;
    }
    if(bytes>0x2800u) {
        LOG(1u,0x30u,0x04000000u,"length > MAX_COMM_EVENT_BUF_SIZE",
            "[sync.module.api]length > MAX_COMM_EVENT_BUF_SIZE");
        return -2;
    }
    uint8_t *node=(uint8_t *)audio_uart_alloc_retry(12u);
    if(node==0) {
        LOG(1u,0x38u,0x04000000u,"malloc failed after retries!",
            "[sync.module.api]malloc failed after retries!");
        return -1;
    }
    audio_uart_buffer_zero(node,12u,0u);
    uint8_t *packet=(uint8_t *)audio_uart_alloc_retry((uint32_t)bytes+8u);
    *(uint8_t **)(void *)(node+8u)=packet;
    if(packet==0) {
        LOG(1u,0x3eu,0x04000000u,"malloc failed after retries!",
            "[sync.module.api]malloc failed after retries!");
        audio_file_heap_free(node);
        return -1;
    }
    *(uint32_t *)(void *)node=context;
    *(uint16_t *)(void *)(node+6u)=(uint16_t)(bytes+8u);
    packet[0]=(uint8_t)target;
    packet[1]=(uint8_t)kind;
    packet[2]=(uint8_t)id;packet[3]=(uint8_t)(id>>8);
    packet[4]=(uint8_t)channel;packet[5]=(uint8_t)(channel>>8);
    packet[6]=(uint8_t)length;packet[7]=(uint8_t)(length>>8);
    if(bytes!=0u && payload!=0)
        (void)audio_queue_copy_bytes(packet+8u,payload,bytes);
    uint8_t role=audio_uart_device_role_get();
    void *queue;
    uint32_t error_line;
    if(role==1u) {
        *(uint16_t *)(void *)(node+4u)=(uint16_t)target;
        LOG(4u,0x53u,0x10400000u,"_pSyncPacketStruct = %p",
            "[sync.module.api]_pSyncPacketStruct = %p",node);
        queue=audio_uart_master_schedule_queue;
        error_line=0x56u;
    }
    else if(role==2u) {
        *(uint16_t *)(void *)(node+4u)=0u;
        queue=g2_uart_send_queue;
        error_line=0x60u;
    }
    else {
        LOG(1u,0x68u,0x04000000u,"GetRoleCacheStatus failed",
            "[sync.module.api]GetRoleCacheStatus failed");
        audio_file_heap_free(packet);
        audio_file_heap_free(node);
        return -1;
    }
    int32_t status=audio_cmsis_queue_put(queue,&node,0u,2000u);
    if(status!=0) {
        LOG(2u,error_line,0x08400000u,
            "send msg to g_syncScheduleMgr_queue failed,errno = %d",
            "[sync.module.api]send msg to g_syncScheduleMgr_queue failed,errno = %d",status);
        audio_file_heap_free(packet);
        audio_file_heap_free(node);
        audio_delay_scheduler_assert();
        for(;;) __asm volatile("nop");
    }
    if(role==2u) (void)osEventFlagsSet(g2_uart_thread_event,2u);
    return 0;
}
