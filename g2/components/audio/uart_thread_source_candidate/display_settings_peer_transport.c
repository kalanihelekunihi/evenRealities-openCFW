/* Native SendDataToPeerExt 0x465480, including ownership and queue failure. */
#include <stdint.h>
struct peer_node {uint32_t correlation;uint16_t kind;uint16_t length;uint8_t *payload;};
_Static_assert(sizeof(struct peer_node)==12u,"peer node ABI");
extern void *audio_settings_peer_send_queue; /* live RAM 0x200749cc */
extern void *audio_settings_peer_event; /* live RAM 0x20074b10 */
extern void *audio_uart_alloc_retry(uint32_t); /* selected 0x4646f0 */
extern void audio_file_heap_free(void *); /* selected 0x474d16 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t); /* selected 0x449abe */
extern uint32_t g2_log_event_set_task(uint32_t,uint32_t); /* selected 0x4495e4 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="sync.module.api";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_interface_api.c";
static const char function[]="SendDataToPeerExt";
static const char null_queue[]="uart send queue is NULL !!!";
static const char null_queue_short[]="[sync.module.api]uart send queue is NULL !!!";
static const char alloc_fail[]="malloc failed after retries!";
static const char alloc_fail_short[]="[sync.module.api]malloc failed after retries!";
static const char send_info[]="SEND_DATA_TO_PEER _pSyncPacketStruct = %p,applictionID = %d,length = %d,eventType = %d";
static const char send_info_short[]="[sync.module.api]SEND_DATA_TO_PEER _pSyncPacketStruct = %p,applictionID = %d,length = %d,eventType = %d";
static const char queue_fail[]="send msg to g_syncScheduleMgr_queue failed,errno = %d";
static const char queue_fail_short[]="[sync.module.api]send msg to g_syncScheduleMgr_queue failed,errno = %d";
static void log_alloc(void) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,path,function,300u,alloc_fail);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x04000000u,alloc_fail_short,alloc_fail_short);
}
int32_t audio_settings_send_peer_packet(uint16_t application,const void *data,uint32_t length,
                                        uint32_t correlation,uint32_t event_type) {
    void *queue=audio_settings_peer_send_queue;
    if(queue==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,292u,null_queue);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,null_queue_short,null_queue_short);
        return -1;
    }
    struct peer_node *node=(struct peer_node *)audio_uart_alloc_retry(12u);
    if(node==0) {log_alloc();return -1;}
    audio_uart_buffer_zero(node,12u,0u);
    uint16_t payload_length=(uint16_t)length;
    node->payload=(uint8_t *)audio_uart_alloc_retry((uint32_t)payload_length+8u);
    if(node->payload==0) {
        log_alloc();audio_file_heap_free(node);return -1;
    }
    node->correlation=correlation;
    node->length=(uint16_t)(payload_length+8u);
    uint8_t *payload=node->payload;
    payload[0]=4u;payload[1]=12u;
    payload[2]=(uint8_t)application;payload[3]=(uint8_t)(application>>8);
    payload[4]=(uint8_t)event_type;payload[5]=(uint8_t)(event_type>>8);
    payload[6]=(uint8_t)payload_length;payload[7]=(uint8_t)(payload_length>>8);
    (void)audio_queue_copy_bytes(payload+8u,data,payload_length);
    node->kind=4u;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,325u,send_info,node,application,
                           payload_length,(uint16_t)event_type);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x11000000u,send_info_short,send_info_short,node,
                                    application,payload_length,(uint16_t)event_type);
    int32_t status=audio_cmsis_queue_put(queue,&node,0u,2000u);
    if(status==0) {
        (void)g2_log_event_set_task((uint32_t)(uintptr_t)audio_settings_peer_event,2u);
        return 0;
    }
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(2u,module,path,function,328u,queue_fail,status);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x08400000u,queue_fail_short,queue_fail_short,status);
    audio_file_heap_free(node->payload);
    audio_file_heap_free(node);
    return -1;
}
