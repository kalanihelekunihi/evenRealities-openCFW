/* Native PB_TxEncodeNotifySecAuthImpl 0x4bb73a, full allocation/encode/send body. */
#include <stdint.h>
struct pb_ostream_candidate {void *callback;void *state;uint32_t max_size;uint32_t bytes_written;const char *errmsg;};
struct pb_msgdesc_candidate;
extern const struct pb_msgdesc_candidate audio_ble_ring_connect_pb_descriptor; /* native 0x7766dc */
extern uint8_t audio_ble_pair_auth_flag_20074ffc; /* live product RAM, initializer unowned */
extern void *file_heap_allocate(uint32_t);
extern void file_heap_free(void *);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern void audio_pb_ostream_from_buffer(struct pb_ostream_candidate *,void *,uint32_t);
extern uint32_t audio_pb_encode(void *,const void *,const void *);
extern uint32_t g2_flashdb_candidate_tick(void);
extern uint32_t audio_ble_notify_direct_475aa6(uint8_t,uint8_t,void *,uint16_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
static const char module[]="pb.devc";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_dev_config\\pb_service_pair_mgr.c";
static const char function[]="PB_TxEncodeNotifySecAuthImpl";
static const char alloc_fail[]="PB_TxEncodeNotifySecAuth alloc fail";
static const char alloc_fail_compact[]="[pb.devc]PB_TxEncodeNotifySecAuth alloc fail";
static const char length_msg[]="PB_TxEncodeNotifySecAuth messageLength = %d";
static const char length_compact[]="[pb.devc]PB_TxEncodeNotifySecAuth messageLength = %d";
static const char encode_fail[]="Encoding failed: %s\n";
static const char encode_fail_compact[]="[pb.devc]Encoding failed: %s\n";
static const char none[]="(none)";
static const char send_fail[]="Thread_MsgPbNotifyDirectByBle fail";
static const char send_fail_compact[]="[pb.devc]Thread_MsgPbNotifyDirectByBle fail";
static void log_line(uint8_t level,uint32_t line,uint32_t mask,const char *message,const char *compact)
{
    if (audio_log_flags()&2u) audio_log_extended(level,module,source,function,line,message);
    uint32_t flags=audio_log_flags();
    if ((flags&1u)||((flags=audio_log_flags())&4u))
        (void)compressed_log_output(mask,compact,compact);
}
uint32_t PB_TxEncodeNotifySecAuthImpl(uint8_t auth)
{
    if (audio_ble_pair_auth_flag_20074ffc==0u) return 0u;
    uint8_t *packet=file_heap_allocate(0x1a8u);
    if (packet==0) {
        log_line(1u,0x8cu,0x04000000u,alloc_fail,alloc_fail_compact);
        return 2u;
    }
    audio_uart_buffer_zero(packet,0x1a8u,0u);
    struct pb_ostream_candidate temp;
    audio_pb_ostream_from_buffer(&temp,packet,0xd4u);
    struct pb_ostream_candidate stream;
    audio_uart_checksum_copy(&stream,&temp,0x14u);
    packet[0xd4u]=4u;
    uint32_t tick=g2_flashdb_candidate_tick();
    packet[0xd6u]=(uint8_t)tick;
    packet[0xd7u]=0u;
    packet[0xd8u]=3u;packet[0xd9u]=0u;
    packet[0xdcu]=(uint8_t)(auth!=0u);
    packet[0xdeu]=0u;
    uint32_t encoded=audio_pb_encode(&stream,&audio_ble_ring_connect_pb_descriptor,packet+0xd4u);
    if (audio_log_flags()&2u)
        audio_log_extended(4u,module,source,function,0x9eu,length_msg,stream.bytes_written);
    uint32_t flags=audio_log_flags();
    if ((flags&1u)||((flags=audio_log_flags())&4u))
        (void)compressed_log_output(0x10400000u,length_compact,length_compact,stream.bytes_written);
    if (!encoded) {
        const char *why=stream.errmsg?stream.errmsg:none;
        if (audio_log_flags()&2u)
            audio_log_extended(1u,module,source,function,0xa1u,encode_fail,why);
        flags=audio_log_flags();
        if ((flags&1u)||((flags=audio_log_flags())&4u))
            (void)compressed_log_output(0x04400000u,encode_fail_compact,encode_fail_compact,why);
        file_heap_free(packet);
        return 0x2bu;
    }
    uint32_t sent=audio_ble_notify_direct_475aa6(1u,0x80u,packet,(uint16_t)stream.bytes_written);
    if (sent==0u) {
        file_heap_free(packet);
        return 0u;
    }
    log_line(1u,0xa7u,0x04000000u,send_fail,send_fail_compact);
    file_heap_free(packet);
    return UINT32_MAX;
}
