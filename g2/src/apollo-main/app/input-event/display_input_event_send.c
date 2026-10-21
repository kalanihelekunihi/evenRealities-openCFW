/* Native SendDataToBoth 0x464d1c, reached from INPM_EventSend 0x4c5916. */
#include <stdint.h>
extern void *audio_uart_sync_schedule_queue; /* pointer cell RAM 0x200749cc */
extern void *audio_uart_input_event_flags; /* pointer cell RAM 0x20074b10 */
extern void *audio_uart_alloc_retry(uint32_t); /* selected 0x4646f0 */
extern void audio_file_heap_free(void *); /* selected 0x474d16 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t); /* selected 0x449abe */
extern uint32_t osEventFlagsSet(void *,uint32_t); /* selected 0x4495e4 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="sync.module.api";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_interface_api.c";
static const char function[]="SendDataToBoth";
#define LOG(level,line,mask,plain,compact,...) do { \
 if(audio_log_level()&2u)audio_log_extended(level,module,path,function,line,plain,##__VA_ARGS__); \
 if((audio_log_level()&1u)||(audio_log_level()&4u)) \
  (void)compressed_log_output(mask,compact,compact,##__VA_ARGS__); \
} while(0)
int32_t audio_uart_input_event_send_464d1c(uint16_t type,const void *payload,uint32_t length,uint32_t context) {
    if(audio_uart_sync_schedule_queue==0) {
        LOG(1u,0x8du,0x04000000u,"uart send queue is NULL !!!",
            "[sync.module.api]uart send queue is NULL !!!");
        return -1;
    }
    uint8_t *node=(uint8_t *)audio_uart_alloc_retry(12u);
    if(node==0) {
        LOG(1u,0x95u,0x04000000u,"malloc failed after retries!",
            "[sync.module.api]malloc failed after retries!");
        return -1;
    }
    audio_uart_buffer_zero(node,12u,0u);
    uint16_t n=(uint16_t)length;
    uint8_t *packet=(uint8_t *)audio_uart_alloc_retry((uint32_t)n+8u);
    *(uint8_t **)(void *)(node+8u)=packet;
    if(packet==0) {
        LOG(1u,0x9bu,0x04000000u,"malloc failed after retries!",
            "[sync.module.api]malloc failed after retries!");
        audio_file_heap_free(node);
        return -1;
    }
    *(uint32_t *)(void *)node=context;
    *(uint16_t *)(void *)(node+6u)=(uint16_t)(n+8u);
    packet[0]=1u;packet[1]=9u;
    packet[2]=(uint8_t)type;packet[3]=(uint8_t)(type>>8);
    packet[4]=0u;packet[5]=0u;
    packet[6]=(uint8_t)n;packet[7]=(uint8_t)(n>>8);
    (void)audio_queue_copy_bytes(packet+8u,payload,n);
    *(uint16_t *)(void *)(node+4u)=1u;
    LOG(4u,0xaeu,0x10400000u,"_pSyncPacketStruct = %p",
        "[sync.module.api]_pSyncPacketStruct = %p",node);
    int32_t status=audio_cmsis_queue_put(audio_uart_sync_schedule_queue,&node,0u,2000u);
    if(status==0) {
        (void)osEventFlagsSet(audio_uart_input_event_flags,2u);
        return 0;
    }
    LOG(2u,0xb1u,0x08400000u,"send msg to g_syncScheduleMgr_queue failed,errno = %d",
        "[sync.module.api]send msg to g_syncScheduleMgr_queue failed,errno = %d",status);
    audio_file_heap_free(packet);
    audio_file_heap_free(node);
    return -1;
}
