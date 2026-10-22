/* Apollo SendInputEventToPeers 0x465748: fixed 12-byte event packet. */
#include <stdint.h>

extern void *g2_uart_send_queue;                 /* RAM 0x200749cc */
extern void *audio_uart_master_schedule_queue;  /* RAM 0x200749d0 */
extern void *g2_uart_thread_event;               /* RAM 0x20074b10 */
extern void *audio_uart_alloc_retry(uint32_t);
extern void audio_file_heap_free(void *);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern uint8_t audio_uart_device_role_get(void);
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t);
extern uint32_t osEventFlagsSet(void *,uint32_t);
extern void audio_delay_scheduler_assert(void);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="sync.module.api";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_interface_api.c";
static const char function[]="SendInputEventToPeers";
#define LOG(level,line,mask,plain,compact,...) do { \
    uint32_t flags=audio_log_level(); \
    if((flags&2u)!=0u) \
        audio_log_extended(level,module,path,function,line,plain,##__VA_ARGS__); \
    flags=audio_log_level(); \
    if((flags&1u)!=0u || (audio_log_level()&4u)!=0u) \
        (void)compressed_log_output(mask,compact,compact,##__VA_ARGS__); \
} while(0)

/* Stock 0x465748 (SendInputEventToPeers) */
int32_t audio_uart_master_input_event(uint32_t device,uint32_t event,
                                       uint32_t value,uint32_t context)
{
    if(g2_uart_send_queue==0) {
        LOG(1u,0x157u,0x04000000u,"uart send queue is NULL !!!",
            "[sync.module.api]uart send queue is NULL !!!");
        return -1;
    }
    uint8_t *node=(uint8_t *)audio_uart_alloc_retry(12u);
    if(node==0) {
        LOG(1u,0x15eu,0x04000000u,"malloc failed after retries!",
            "[sync.module.api]malloc failed after retries!");
        return -1;
    }
    audio_uart_buffer_zero(node,12u,0u);
    uint8_t *packet=(uint8_t *)audio_uart_alloc_retry(12u);
    *(uint8_t **)(void *)(node+8u)=packet;
    if(packet==0) {
        LOG(1u,0x165u,0x04000000u,"malloc failed after retries!",
            "[sync.module.api]malloc failed after retries!");
        audio_file_heap_free(node);
        return -1;
    }
    *(uint32_t *)(void *)node=context;
    *(uint16_t *)(void *)(node+6u)=12u;
    packet[0]=3u;packet[1]=7u;
    packet[2]=(uint8_t)device;packet[3]=(uint8_t)(device>>8);
    packet[4]=(uint8_t)event;packet[5]=(uint8_t)(event>>8);
    packet[6]=(uint8_t)(event>>16);packet[7]=(uint8_t)(event>>24);
    packet[8]=(uint8_t)value;packet[9]=(uint8_t)(value>>8);
    packet[10]=(uint8_t)(value>>16);packet[11]=(uint8_t)(value>>24);
    uint8_t role=audio_uart_device_role_get();
    void *queue;
    uint32_t error_line;
    if(role==1u) {
        *(uint16_t *)(void *)(node+4u)=3u;
        LOG(4u,0x17eu,0x11000000u,
            "SEND_INPUT_EVENT_TO_PEERS _pSyncPacketStruct = %p,InputDevType = %d,eventID = %d,eventValue = %d",
            "[sync.module.api]SEND_INPUT_EVENT_TO_PEERS _pSyncPacketStruct = %p,InputDevType = %d,eventID = %d,eventValue = %d",
            node,(uint16_t)device,event,value);
        queue=audio_uart_master_schedule_queue;
        error_line=0x181u;
    }
    else if(role==2u) {
        *(uint16_t *)(void *)(node+4u)=0u;
        LOG(4u,0x189u,0x10400000u,
            "SEND_INPUT_EVENT_TO_PEERS _pSyncPacketStruct = %p",
            "[sync.module.api]SEND_INPUT_EVENT_TO_PEERS _pSyncPacketStruct = %p",node);
        queue=g2_uart_send_queue;
        error_line=0x18cu;
    }
    else {
        LOG(1u,0x194u,0x04000000u,"GetRoleCacheStatus failed",
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
