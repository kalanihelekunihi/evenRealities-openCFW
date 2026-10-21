/* Native Thread_MsgTxByBle 0x47564e: allocation, four wire layouts,
 * ESS backpressure, queue dispatch, and ownership on every exit. */
#include <stdint.h>
struct ble_msgtx_manager {uint8_t reserved[8];void *thread;void *queue;};
_Static_assert(sizeof(struct ble_msgtx_manager)==16u,"BLE manager ABI");
extern struct ble_msgtx_manager audio_ble_msgtx_manager; /* live struct RAM 0x20004020 */
extern void *codec_allocate(uint32_t); /* selected native 0x474cd2 */
extern void audio_file_heap_free(void *); /* selected native 0x474d16 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t); /* selected 0x449abe */
extern uint32_t audio_cmsis_queue_get_count(void *); /* native 0x449bc8 */
extern uint32_t audio_cmsis_queue_get_capacity(void *); /* native 0x449bbc */
extern uint32_t audio_thread_flags_set(void *,uint32_t); /* selected 0x449238 */
extern uint32_t audio_ble_is_connected(void); /* native ble_msgtx_isConnected */
extern void audio_ble_set_fast_mode(void); /* native APP_ConnectParamESSSetFastMode */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.msgtx";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ble_msgtx.c";
static const char function[]="_dispatchMsgTxByBle";
static const char null_msg[]="msg dispatch msg buffer is null";
static const char null_short[]="[ble.msgtx]msg dispatch msg buffer is null";
static const char queue_msg[]="Thread_MsgFromOther queue null";
static const char queue_short[]="[ble.msgtx]Thread_MsgFromOther queue null";
static const char fast_msg[]="pipingType = BLE_PIPE_ESS, !APP_IsConnectParamFastMode()";
static const char fast_short[]="[ble.msgtx]pipingType = BLE_PIPE_ESS, !APP_IsConnectParamFastMode()";
static const char alloc_msg[]="_dispatchMsgTxByBle alloc fail";
static const char alloc_short[]="[ble.msgtx]_dispatchMsgTxByBle alloc fail";
static const char type_msg[]="pipingType = %d error";
static const char type_short[]="[ble.msgtx]pipingType = %d error";
static const char count_msg[]="tx msg_count = %d, msg_capacity = %d";
static const char count_short[]="[ble.msgtx]tx msg_count = %d, msg_capacity = %d";
static const char full_msg[]="ESS queue full (%d/%d), dropping new message (old messages will be processed)";
static const char full_short[]="[ble.msgtx]ESS queue full (%d/%d), dropping new message (old messages will be processed)";
static const char put_msg[]="msg ble tx dispatch send msg, status = %d";
static const char put_short[]="[ble.msgtx]msg ble tx dispatch send msg, status = %d";
static void log_plain(uint8_t severity,uint32_t line,uint32_t mask,uint32_t compressed,
                      const char *message,const char *short_message) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(severity,module,path,function,line,message);
    if((audio_log_flags()&mask)!=0u)
        (void)compressed_log_output(compressed,short_message,short_message);
}
static void log_one(uint8_t severity,uint32_t line,uint32_t mask,uint32_t compressed,
                    const char *message,const char *short_message,uint32_t value) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(severity,module,path,function,line,message,value);
    if((audio_log_flags()&mask)!=0u)
        (void)compressed_log_output(compressed,short_message,short_message,value);
}
static void log_two(uint8_t severity,uint32_t line,uint32_t mask,uint32_t compressed,
                    const char *message,const char *short_message,uint32_t a,uint32_t b) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(severity,module,path,function,line,message,a,b);
    if((audio_log_flags()&mask)!=0u)
        (void)compressed_log_output(compressed,short_message,short_message,a,b);
}
static void store32(uint8_t *p,uint32_t v) {
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);
}
uint32_t audio_ble_msg_tx(uint8_t piping,uint8_t service,uint8_t type,uint8_t command,
                          const void *payload,uint16_t length) {
    struct ble_msgtx_manager *manager=&audio_ble_msgtx_manager;
    if(payload==0) {
        log_plain(1u,305u,5u,0x04000000u,null_msg,null_short);
        return UINT32_MAX;
    }
    if(manager->queue==0) {
        log_plain(1u,310u,5u,0x04000000u,queue_msg,queue_short);
        return UINT32_MAX;
    }
    if(piping==1u&&audio_ble_is_connected()==0u) {
        log_plain(2u,315u,5u,0x08000000u,fast_msg,fast_short);
        audio_ble_set_fast_mode();
    }
    uint8_t *node=(uint8_t *)codec_allocate(((uint32_t)length+14u)&~3u);
    if(node==0) {
        log_plain(1u,324u,5u,0x04000000u,alloc_msg,alloc_short);
        return UINT32_MAX;
    }
    if(piping==0u||piping==2u||piping==3u) {
        store32(node,piping==0u?1u:piping==2u?4u:8u);
        store32(node+4u,(uint32_t)length+3u);
        node[8]=service;node[9]=type;node[10]=command;
        (void)audio_queue_copy_bytes(node+11u,payload,length);
    } else if(piping==1u) {
        store32(node,2u);store32(node+4u,length);
        (void)audio_queue_copy_bytes(node+8u,payload,length);
    } else {
        log_one(1u,371u,5u,0x04400000u,type_msg,type_short,piping);
    }
    uint32_t count=audio_cmsis_queue_get_count(manager->queue);
    uint32_t capacity=audio_cmsis_queue_get_capacity(manager->queue);
    if(piping!=1u)
        log_two(4u,379u,5u,0x10800000u,count_msg,count_short,count,capacity);
    if(piping==1u&&(capacity>>1u)<=count) {
        log_two(2u,385u,5u,0x08800000u,full_msg,full_short,count,capacity);
        audio_file_heap_free(node);
        return 0u;
    }
    int32_t status=audio_cmsis_queue_put(manager->queue,&node,0u,500u);
    if(status==0) {
        (void)audio_thread_flags_set(manager->thread,0x400000u);
        return 0u;
    }
    log_one(1u,393u,5u,0x04400000u,put_msg,put_short,(uint32_t)status);
    audio_file_heap_free(node);
    return UINT32_MAX;
}
