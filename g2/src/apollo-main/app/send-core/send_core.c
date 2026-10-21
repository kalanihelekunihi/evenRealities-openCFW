/* SendDataToPeer 0x4651e0 and SendDataToPeerExt 0x465480. Both allocate a
 * 12-byte scheduler node and a length+8 protocol packet, then enqueue it. */
#include <stdint.h>
extern void *g2_uart_send_queue; /* RAM0x200749cc */
extern void *g2_uart_thread_event; /* RAM0x20074b10 */
extern void *audio_uart_alloc_retry(uint32_t); /* 0x4646f0 */
extern void audio_file_heap_free(void *); /* selected 0x474d16 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t); /* 0x449abe */
extern uint32_t g2_log_event_set_task(uint32_t,uint32_t); /* 0x4495e4 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="sync.module.api";
static const char source_file[]=
 "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_interface_api.c";
static const char request_function[]="SendDataToPeer";
static const char extended_function[]="SendDataToPeerExt";
static const char queue_missing[]="uart send queue is NULL !!!";
static const char queue_missing_short[]="[sync.module.api]uart send queue is NULL !!!";
static const char alloc_failed[]="malloc failed after retries!";
static const char alloc_failed_short[]="[sync.module.api]malloc failed after retries!";
static const char queued[]=
 "SEND_DATA_TO_PEER _pSyncPacketStruct = %p,applictionID = %d,length = %d";
static const char queued_short[]=
 "[sync.module.api]SEND_DATA_TO_PEER _pSyncPacketStruct = %p,applictionID = %d,length = %d";
static const char queued_ext[]=
 "SEND_DATA_TO_PEER _pSyncPacketStruct = %p,applictionID = %d,length = %d,eventType = %d";
static const char queued_ext_short[]=
 "[sync.module.api]SEND_DATA_TO_PEER _pSyncPacketStruct = %p,applictionID = %d,length = %d,eventType = %d";
static const char enqueue_failed[]=
 "send msg to g_syncScheduleMgr_queue failed,errno = %d";
static const char enqueue_failed_short[]=
 "[sync.module.api]send msg to g_syncScheduleMgr_queue failed,errno = %d";

typedef struct {uint32_t id;uint16_t type;uint16_t size;uint8_t *payload;} send_node;
_Static_assert(sizeof(send_node)==12,"native sync send node size");
static void log_plain(uint8_t level,uint32_t line,const char *function,
                      const char *message,const char *short_message) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,module,source_file,function,line,message);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output((uint32_t)level<<26,short_message,
                                    short_message);
}
static void log_enqueued(const char *function,uint32_t line,send_node *node,
                         uint16_t app,uint16_t size,uint16_t event,
                         uint32_t extended) {
    if(extended) {
        if(audio_log_flags()&2u)
            audio_log_extended(4u,module,source_file,function,line,queued_ext,
                               node,app,size,event);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x11000000u,queued_ext_short,
                                        queued_ext_short,node,app,size,event);
    } else {
        if(audio_log_flags()&2u)
            audio_log_extended(4u,module,source_file,function,line,queued,
                               node,app,size);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x10c00000u,queued_short,
                                        queued_short,node,app,size);
    }
}
static void log_enqueue_failure(const char *function,uint32_t line,int32_t status) {
    if(audio_log_flags()&2u)
        audio_log_extended(2u,module,source_file,function,line,
                           enqueue_failed,status);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x08400000u,enqueue_failed_short,
                                    enqueue_failed_short,status);
}
static uint32_t send_core(uint16_t app,const void *bytes,uint32_t length,
                          uint32_t id,uint16_t event,uint32_t extended) {
    const char *function=extended?extended_function:request_function;
    if(g2_uart_send_queue==0) {
        log_plain(1u,extended?0x124u:0xf2u,function,
                  queue_missing,queue_missing_short);
        return UINT32_MAX;
    }
    send_node *node=audio_uart_alloc_retry(12u);
    if(node==0) {
        log_plain(1u,extended?300u:0xfau,function,
                  alloc_failed,alloc_failed_short);
        return UINT32_MAX;
    }
    node->id=0u;node->type=0u;node->size=0u;node->payload=0;
    uint16_t n=(uint16_t)length;
    node->payload=audio_uart_alloc_retry((uint32_t)n+8u);
    if(node->payload==0) {
        log_plain(1u,extended?0x132u:0x100u,function,
                  alloc_failed,alloc_failed_short);
        audio_file_heap_free(node);
        return UINT32_MAX;
    }
    node->id=id;
    node->type=4u;
    node->size=(uint16_t)(n+8u);
    uint8_t *packet=node->payload;
    packet[0]=4u;packet[1]=12u;
    packet[2]=(uint8_t)app;packet[3]=(uint8_t)(app>>8);
    packet[4]=(uint8_t)event;packet[5]=(uint8_t)(event>>8);
    packet[6]=(uint8_t)n;packet[7]=(uint8_t)(n>>8);
    (void)audio_queue_copy_bytes(packet+8u,bytes,n);
    log_enqueued(function,extended?0x145u:0x113u,node,app,n,event,extended);
    int32_t status=audio_cmsis_queue_put(g2_uart_send_queue,&node,0u,2000u);
    if(status==0) {
        (void)g2_log_event_set_task((uint32_t)(uintptr_t)g2_uart_thread_event,2u);
        return 0u;
    }
    log_enqueue_failure(function,extended?0x148u:0x116u,status);
    audio_file_heap_free(node->payload);
    audio_file_heap_free(node);
    return UINT32_MAX;
}
uint32_t audio_uart_request_send(uint32_t app,const void *bytes,uint32_t length,
                                  uint32_t id) {
    return send_core((uint16_t)app,bytes,length,id,0u,0u);
}
uint32_t audio_uart_handshake_send(uint32_t app,const void *bytes,uint32_t length,
                                    uint32_t id,uint32_t event) {
    return send_core((uint16_t)app,bytes,length,id,(uint16_t)event,1u);
}
