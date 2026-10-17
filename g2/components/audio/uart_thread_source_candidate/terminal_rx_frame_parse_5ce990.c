/* Terminal connection frame parser, stock 0x5ce990..0x5ceaeb. */
#include <stdint.h>

struct terminal_pb_stream_5ce990 {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *errmsg;
};
_Static_assert(sizeof(struct terminal_pb_stream_5ce990)==16u,"nanopb stream ABI");

extern const uint8_t audio_terminal_tx_pb_descriptor[];
extern uint8_t audio_terminal_message_sequence;
#ifdef OPENCFW_ORACLE_EXTERNAL_RX_TICK
extern uint32_t audio_terminal_rx_last_tick_20074874;
#else
uint32_t audio_terminal_rx_last_tick_20074874
    __attribute__((section(".bss.opencfw.terminal.rx_last_tick"),used,aligned(4)));
#endif
extern void audio_uart_pb_stream_init(struct terminal_pb_stream_5ce990 *,const void *,uint32_t);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern uint32_t audio_uart_pb_decode(void *,const void *,void *);
extern uint32_t g2_flashdb_candidate_tick(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="pb.terminal";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_terminal\\pb_service_terminal.c";
static const char function[]="APP_PbTerminalRxFrameDataProcess";
static const char invalid[]="terminal rx parameter is null";
static const char invalid_short[]="[pb.terminal]terminal rx parameter is null";
static const char decode_failed[]="terminal decode failed: %s";
static const char decode_failed_short[]="[pb.terminal]terminal decode failed: %s";
static const char duplicate[]="terminal duplicate packet: magic=%d elapsed=%lu";
static const char duplicate_short[]="[pb.terminal]terminal duplicate packet: magic=%d elapsed=%lu";
static const char none[]="(none)";

uint32_t audio_registry_ring_connect_parse_5ce990(const void *data,
                                                   uint32_t length,
                                                   uint8_t *message) {
    if (data==0 || message==0) {
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,0x70u,invalid);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,invalid_short,invalid_short);
        return 6u;
    }
    struct terminal_pb_stream_5ce990 initial,stream;
    audio_uart_pb_stream_init(&initial,data,(uint16_t)length);
    audio_uart_checksum_copy(&stream,&initial,16u);
    if ((uint8_t)audio_uart_pb_decode(&stream,audio_terminal_tx_pb_descriptor,
                                      message)==0u) {
        const char *error=stream.errmsg!=0?stream.errmsg:none;
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,0x77u,decode_failed,error);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04400000u,decode_failed_short,
                                        decode_failed_short,error);
        return 5u;
    }
    uint32_t tick=g2_flashdb_candidate_tick();
    uint32_t elapsed=tick-audio_terminal_rx_last_tick_20074874;
    if (message[1]==audio_terminal_message_sequence && elapsed<3000u) {
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x7eu,duplicate,
                               message[1],elapsed);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08800000u,duplicate_short,
                                        duplicate_short,message[1],elapsed);
        return 13u;
    }
    audio_terminal_message_sequence=message[1];
    audio_terminal_rx_last_tick_20074874=tick;
    return 0u;
}
