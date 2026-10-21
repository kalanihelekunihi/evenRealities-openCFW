/* Apollo SendStartUpCommandtoScheduleManager 0x465d7c. */
#include <stdint.h>

extern void *g2_uart_send_queue;                /* RAM 0x200749cc */
extern void *audio_uart_master_schedule_queue; /* RAM 0x200749d0 */
extern void *audio_uart_alloc_retry(uint32_t);
extern void audio_file_heap_free(void *);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern uint8_t audio_uart_device_role_get(void);
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t);
extern void audio_delay_scheduler_assert(void);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="sync.module.api";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_interface_api.c";
static const char function[]="SendStartUpCommandtoScheduleManager";
#define LOG(level,line,mask,plain,compact,...) do { \
    uint32_t flags=audio_log_level(); \
    if((flags&2u)!=0u) \
        audio_log_extended(level,module,path,function,line,plain,##__VA_ARGS__); \
    flags=audio_log_level(); \
    if((flags&1u)!=0u || (audio_log_level()&4u)!=0u) \
        (void)compressed_log_output(mask,compact,compact,##__VA_ARGS__); \
} while(0)

int32_t audio_uart_display_channel_set(uint32_t channel)
{
    if(audio_uart_device_role_get()!=1u) return -1;
    if(g2_uart_send_queue==0) {
        LOG(1u,0x1e4u,0x04000000u,"uart send queue is NULL !!!",
            "[sync.module.api]uart send queue is NULL !!!");
        return -1;
    }
    uint8_t *node=(uint8_t *)audio_uart_alloc_retry(12u);
    if(node==0) {
        LOG(1u,0x1ecu,0x04000000u,"malloc failed after retries!",
            "[sync.module.api]malloc failed after retries!");
        return -1;
    }
    audio_uart_buffer_zero(node,12u,0u);
    uint8_t *packet=(uint8_t *)audio_uart_alloc_retry(8u);
    *(uint8_t **)(void *)(node+8u)=packet;
    if(packet==0) {
        LOG(1u,0x1f2u,0x04000000u,"malloc failed after retries!",
            "[sync.module.api]malloc failed after retries!");
        audio_file_heap_free(node);
        return -1;
    }
    *(uint32_t *)(void *)node=0u;
    *(uint16_t *)(void *)(node+6u)=8u;
    packet[0]=5u;packet[1]=0x0fu;
    packet[2]=(uint8_t)channel;packet[3]=(uint8_t)(channel>>8);
    for(uint32_t i=4u;i<8u;i++) packet[i]=0u;
    if(audio_uart_device_role_get()!=1u) return 0;
    *(uint16_t *)(void *)(node+4u)=5u;
    LOG(4u,0x205u,0x10400000u,
        "SEND_START_UP_COMMAND_TO_SCHEDULE_MANAGER _pSyncPacketStruct = %p",
        "[sync.module.api]SEND_START_UP_COMMAND_TO_SCHEDULE_MANAGER _pSyncPacketStruct = %p",node);
    int32_t status=audio_cmsis_queue_put(audio_uart_master_schedule_queue,&node,0u,2000u);
    if(status!=0) {
        LOG(2u,0x208u,0x08400000u,
            "send msg to g_syncScheduleMgr_queue failed,errno = %d",
            "[sync.module.api]send msg to g_syncScheduleMgr_queue failed,errno = %d",status);
        audio_file_heap_free(packet);
        audio_file_heap_free(node);
        audio_delay_scheduler_assert();
        for(;;) __asm volatile("nop");
    }
    return 0;
}
