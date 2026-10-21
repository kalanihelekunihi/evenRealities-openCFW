/* Native APP_PbTxEncodeNotifAppIDNotInWhitelist 0x4d71bc. The nanopb
 * descriptor at stock 0x7799f4 remains a typed source-data contract. */
#include <stdint.h>
struct pb_ostream_candidate {void *callback;void *state;uint32_t max_size;uint32_t bytes_written;const char *errmsg;};
_Static_assert(sizeof(struct pb_ostream_candidate)==20u,"nanopb ostream ABI");
struct pb_msgdesc_candidate {const uint32_t *field_info;const struct pb_msgdesc_candidate *const *submsg_info;
    const uint8_t *default_value;uint8_t (*field_callback)(void *,void *,const void *);
    uint16_t field_count,required_field_count,largest_tag;};
extern void *file_heap_allocate(uint32_t);
extern void file_heap_free(void *);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern uint32_t g2_log_module_length(const char *);
extern uint32_t g2_flashdb_candidate_tick(void);
extern void audio_pb_ostream_from_buffer(struct pb_ostream_candidate *,void *,uint32_t);
extern uint32_t audio_pb_encode(void *,const void *,const void *);
extern uint32_t audio_settings_notify_ble(uint8_t,uint8_t,const void *,uint32_t);
extern const struct pb_msgdesc_candidate audio_ble_ancc_not_whitelisted_pb_descriptor; /* ROM 0x7799f4 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
static const char module[]="pb.notif";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_notification\\pb_service_notification.c";
static const char fn[]="APP_PbTxEncodeNotifAppIDNotInWhitelist";
static void log0(uint8_t level,uint32_t line,const char *plain,uint32_t code,const char *compact){
    if(audio_log_level()&2u)audio_log_extended(level,module,path,fn,line,plain);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(code,compact,compact);
}
static void log1(uint8_t level,uint32_t line,const char *plain,uint32_t code,const char *compact,uint32_t v){
    if(audio_log_level()&2u)audio_log_extended(level,module,path,fn,line,plain,v);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(code,compact,compact,v);
}
static void put16(uint8_t *p,uint16_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}

uint32_t audio_ble_ancc_not_whitelisted_4d71bc(const uint8_t *id,const uint8_t *name){
    uint8_t *packet=(uint8_t *)file_heap_allocate(0x9cu);
    if(packet==0){
        static const char fail[]="PB_TxEncodeNotifyBleConnectParams alloc fail";
        static const char short_fail[]="[pb.notif]PB_TxEncodeNotifyBleConnectParams alloc fail";
        log0(1u,200u,fail,0x04000000u,short_fail);return 2u;
    }
    audio_uart_buffer_zero(packet,0x9cu,0u);
    struct pb_ostream_candidate temp;
    audio_pb_ostream_from_buffer(&temp,packet,0x4eu);
    struct pb_ostream_candidate stream=temp;
    packet[0x4eu]=2u;
    packet[0x4fu]=(uint8_t)g2_flashdb_candidate_tick();
    put16(packet+0x50u,4u);
    uint32_t id_len=g2_log_module_length((const char *)id);
    audio_queue_copy_bytes(packet+0x54u,id,id_len+1u);
    put16(packet+0x52u,(uint16_t)(id_len+1u));
    uint32_t name_len=g2_log_module_length((const char *)name);
    audio_queue_copy_bytes(packet+0x76u,name,name_len+1u);
    put16(packet+0x74u,(uint16_t)(name_len+1u));
    packet[0x96u]=0u;
    uint32_t encoded=audio_pb_encode(&stream,&audio_ble_ancc_not_whitelisted_pb_descriptor,packet+0x4eu);
    static const char length_msg[]="messageLength = %d";
    static const char length_short[]="[pb.notif]messageLength = %d";
    log1(4u,0xdfu,length_msg,0x10400000u,length_short,stream.bytes_written);
    if(encoded==0u){
        static const char msg[]="Encoding failed: %s\n";
        static const char compact[]="[pb.notif]Encoding failed: %s\n";
        const char *error=stream.errmsg!=0?stream.errmsg:"(none)";
        if(audio_log_level()&2u)audio_log_extended(1u,module,path,fn,0xe2u,msg,error);
        if((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x04400000u,compact,compact,error);
        file_heap_free(packet);return 0x2bu;
    }
    uint32_t status=audio_settings_notify_ble(1u,4u,packet,stream.bytes_written&0xffffu);
    if(status!=0u){
        static const char fail[]="Thread_MsgPbNotifyByBle fail";
        static const char short_fail[]="[pb.notif]Thread_MsgPbNotifyByBle fail";
        log0(1u,0xe8u,fail,0x04000000u,short_fail);
        file_heap_free(packet);return UINT32_MAX;
    }
    file_heap_free(packet);return 0u;
}
