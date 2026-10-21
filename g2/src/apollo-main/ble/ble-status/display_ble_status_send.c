/* Native SendDataToBoth 0x464d1c: owned 12-byte node and framed payload. */
#include <stdint.h>
struct audio_ble_status_node {
    uint32_t correlation;
    uint16_t kind;
    uint16_t length;
    uint8_t *payload;
};
_Static_assert(sizeof(struct audio_ble_status_node)==12u,"status node ABI");
extern void *audio_settings_peer_send_queue; /* RAM 0x200749cc */
extern void *audio_settings_peer_event; /* RAM 0x20074b10 */
extern void *audio_uart_alloc_retry(uint32_t); /* 0x4646f0 */
extern void audio_file_heap_free(void *); /* 0x474d16 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* 0x439be4 */
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t); /* 0x449abe */
extern uint32_t g2_log_event_set_task(uint32_t,uint32_t); /* 0x4495e4 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="sync.module.api";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_interface_api.c";
static const char function[]="SendDataToBoth";
static void allocation_failed(void) {
    if(audio_log_level()&2u)
        audio_log_extended(1u,module,source,function,0x95u,"malloc failed after retries!");
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x04000000u,"[sync.module.api]malloc failed after retries!","[sync.module.api]malloc failed after retries!");
}
int32_t audio_ble_send_status_message(uint32_t application,const uint8_t *data,
                                      uint32_t length,uint32_t correlation) {
    void *queue=audio_settings_peer_send_queue;
    if(queue==0) {
        if(audio_log_level()&2u)
            audio_log_extended(1u,module,source,function,0x8du,"uart send queue is NULL !!!");
        if((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x04000000u,"[sync.module.api]uart send queue is NULL !!!","[sync.module.api]uart send queue is NULL !!!");
        return -1;
    }
    struct audio_ble_status_node *node=(struct audio_ble_status_node *)audio_uart_alloc_retry(12u);
    if(node==0) {allocation_failed();return -1;}
    audio_uart_buffer_zero(node,12u,0u);
    uint16_t payload_length=(uint16_t)length;
    node->payload=(uint8_t *)audio_uart_alloc_retry((uint32_t)payload_length+8u);
    if(node->payload==0) {
        allocation_failed();audio_file_heap_free(node);return -1;
    }
    node->correlation=correlation;
    node->length=(uint16_t)(length+8u);
    uint8_t *payload=node->payload;
    payload[0]=1u;payload[1]=9u;
    payload[2]=(uint8_t)application;payload[3]=(uint8_t)(application>>8);
    payload[4]=0u;payload[5]=0u;
    payload[6]=(uint8_t)length;payload[7]=(uint8_t)(length>>8);
    (void)audio_queue_copy_bytes(payload+8u,data,payload_length);
    node->kind=1u;
    if(audio_log_level()&2u)
        audio_log_extended(4u,module,source,function,0xaeu,"_pSyncPacketStruct = %p",node);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x10400000u,"[sync.module.api]_pSyncPacketStruct = %p","[sync.module.api]_pSyncPacketStruct = %p",node);
    int32_t status=audio_cmsis_queue_put(queue,&node,0u,2000u);
    if(status==0) {
        (void)g2_log_event_set_task((uint32_t)(uintptr_t)audio_settings_peer_event,2u);
        return 0;
    }
    if(audio_log_level()&2u)
        audio_log_extended(2u,module,source,function,0xb1u,
            "send msg to g_syncScheduleMgr_queue failed,errno = %d",status);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x08400000u,
            "[sync.module.api]send msg to g_syncScheduleMgr_queue failed,errno = %d",
            "[sync.module.api]send msg to g_syncScheduleMgr_queue failed,errno = %d",status);
    audio_file_heap_free(node->payload);
    audio_file_heap_free(node);
    return -1;
}
