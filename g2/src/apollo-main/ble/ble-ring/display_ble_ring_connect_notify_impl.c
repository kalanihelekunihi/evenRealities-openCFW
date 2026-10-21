/* Product PB_TxEncodeNotifyRingConnectInfoImpl 0x4bc1b4.  Nanopb and BLE
 * transport remain genuine lower contracts, not substituted success paths. */
#include <stdint.h>
struct pb_ostream_candidate {void *callback;void *state;uint32_t max_size;uint32_t bytes_written;const char *errmsg;};
_Static_assert(sizeof(struct pb_ostream_candidate)==20u,"nanopb ostream ABI");
extern void *file_heap_allocate(uint32_t);
extern void file_heap_free(void *);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern void audio_pb_ostream_from_buffer(struct pb_ostream_candidate *,void *,uint32_t);
extern uint32_t audio_pb_encode(struct pb_ostream_candidate *,const void *,const void *);
struct pb_msgdesc_candidate;
extern const struct pb_msgdesc_candidate audio_ble_ring_connect_pb_descriptor; /* ROM 0x7766dc */
extern uint32_t g2_flashdb_candidate_tick(void);
extern void audio_uart_ring_target_addr_copy_4a2190(uint8_t *,uint32_t);
extern uint32_t audio_ble_master_auth_mode_set(uint8_t);
extern void audio_ble_master_clear_failure_notify(void);
extern void audio_ble_slave_security_state(uint8_t);
extern uint32_t audio_ble_notify_direct_475aa6(uint8_t,uint8_t,void *,uint16_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
static const char module[]="pb.devc";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_dev_config\\pb_service_pair_mgr.c";
static const char function[]="PB_TxEncodeNotifyRingConnectInfoImpl";
static const char alloc_fail[]="PB_TxEncodeNotifyRingConnectInfo alloc fail";
static const char alloc_fail_compact[]="[pb.devc]PB_TxEncodeNotifyRingConnectInfo alloc fail";
static const char conn_ret[]="PB_TxEncodeNotifyRingConnectInfo connRet = %d";
static const char conn_ret_compact[]="[pb.devc]PB_TxEncodeNotifyRingConnectInfo connRet = %d";
static const char length_msg[]="messageLength = %d";
static const char length_compact[]="[pb.devc]messageLength = %d";
static const char encode_fail[]="Encoding failed: %s\n";
static const char encode_fail_compact[]="[pb.devc]Encoding failed: %s\n";
static const char none[]="(none)";
static const char send_fail[]="NotifyRingConn Thread_MsgPbNotifyDirectByBle fail";
static const char send_fail_compact[]="[pb.devc]NotifyRingConn Thread_MsgPbNotifyDirectByBle fail";
static void put16(uint8_t *p,uint16_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8u);}
static void log_line(uint8_t level,uint32_t line,uint32_t mask,const char *message,const char *compact){
    if (audio_log_flags()&2u) audio_log_extended(level,module,source,function,line,message);
    uint32_t flags=audio_log_flags();
    if ((flags&1u)||((flags=audio_log_flags())&4u))
        (void)compressed_log_output(mask,compact,compact);
}
uint32_t PB_TxEncodeNotifyRingConnectInfoImpl(uint8_t connection_result)
{
    uint8_t *packet=(uint8_t *)file_heap_allocate(0x1a8u);
    if (!packet) {
        log_line(1u,0x19cu,0x04000000u,alloc_fail,alloc_fail_compact);
        return 2u;
    }
    audio_uart_buffer_zero(packet,0x1a8u,0u);
    struct pb_ostream_candidate temp;
    audio_pb_ostream_from_buffer(&temp,packet,0xd4u);
    struct pb_ostream_candidate stream;
    audio_uart_checksum_copy(&stream,&temp,0x14u);
    packet[0xd4u]=6u;
    put16(packet+0xd6u,(uint8_t)g2_flashdb_candidate_tick());
    put16(packet+0xd8u,5u);
    audio_uart_ring_target_addr_copy_4a2190(packet+0xe0u,(uint32_t)(uintptr_t)(packet+0xe8u));
    packet[0xdcu]=(uint8_t)audio_ble_master_auth_mode_set(0x5au);
    (void)audio_ble_master_auth_mode_set(0u);
    packet[0xf8u]=connection_result;
    if (packet[0xf8u]==0u) audio_ble_master_clear_failure_notify();
    else audio_ble_slave_security_state(2u);
    if (audio_log_flags()&2u)
        audio_log_extended(4u,module,source,function,0x1b5u,conn_ret,packet[0xf8u]);
    uint32_t flags=audio_log_flags();
    if ((flags&1u)||((flags=audio_log_flags())&4u))
        (void)compressed_log_output(0x10400000u,conn_ret_compact,conn_ret_compact,packet[0xf8u]);
    packet[0xf9u]=0u;
    uint32_t encoded=audio_pb_encode(&stream,&audio_ble_ring_connect_pb_descriptor,packet+0xd4u);
    if (audio_log_flags()&2u)
        audio_log_extended(4u,module,source,function,0x1bbu,length_msg,stream.bytes_written);
    flags=audio_log_flags();
    if ((flags&1u)||((flags=audio_log_flags())&4u))
        (void)compressed_log_output(0x10400000u,length_compact,length_compact,stream.bytes_written);
    if (!encoded) {
        const char *why=stream.errmsg?stream.errmsg:none;
        if (audio_log_flags()&2u)
            audio_log_extended(1u,module,source,function,0x1beu,encode_fail,why);
        flags=audio_log_flags();
        if ((flags&1u)||((flags=audio_log_flags())&4u))
            (void)compressed_log_output(0x04400000u,encode_fail_compact,encode_fail_compact,why);
        file_heap_free(packet);
        return 0x2bu;
    }
    uint32_t sent=audio_ble_notify_direct_475aa6(1u,0x80u,packet,(uint16_t)stream.bytes_written);
    if (sent!=0u) {
        log_line(1u,0x1c4u,0x04000000u,send_fail,send_fail_compact);
        file_heap_free(packet);
        return UINT32_MAX;
    }
    file_heap_free(packet);
    return 0u;
}
