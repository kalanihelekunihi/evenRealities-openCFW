/* Terminal query-reply packet sender, stock 0x5ced38..0x5cee07. */
#include <stdint.h>

extern uint8_t audio_terminal_message_sequence;
extern uint32_t audio_terminal_send_message_5ce7c4(uint32_t,uint32_t,const void *,uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="pb.terminal";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_terminal\\pb_service_terminal.c";
static const char function[]="APP_PbTerminalTxEncodeQueryReply";
static const char null_message[]="terminal query reply is null";
static const char null_short[]="[pb.terminal]terminal query reply is null";
static const char reply[]="terminal query reply: magic=%d query_id=%lu option_id=%lu";
static const char reply_short[]="[pb.terminal]terminal query reply: magic=%d query_id=%lu option_id=%lu";

uint32_t audio_terminal_query_reply_send_5ced38(const uint32_t *packet) {
    if (packet==0) {
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,0xb9u,null_message);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,null_short,null_short);
        return 6u;
    }
    uint32_t magic=(uint32_t)audio_terminal_message_sequence+1u;
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0xbdu,reply,
                           magic,packet[0],packet[1]);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0cc00000u,reply_short,reply_short,
                                    magic,packet[0],packet[1]);
    return audio_terminal_send_message_5ce7c4(0xa3u,11u,packet,(uint8_t)magic,1u);
}
