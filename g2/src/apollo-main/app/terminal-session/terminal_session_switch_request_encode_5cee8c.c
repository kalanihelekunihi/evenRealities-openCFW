/* Terminal session-switch request packet encoder, stock 0x5cee8c..0x5cef12. */
#include <stdint.h>

extern uint8_t audio_terminal_message_sequence;
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern uint32_t audio_terminal_send_message_5ce7c4(uint32_t,uint32_t,const void *,uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="pb.terminal";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_terminal\\pb_service_terminal.c";
static const char function[]="APP_PbTerminalTxEncodeSessionSwitchRequest";
static const char message[]="terminal session switch request: magic=%d host=%lu session=%lu";
static const char short_message[]="[pb.terminal]terminal session switch request: magic=%d host=%lu session=%lu";

uint32_t audio_terminal_session_switch_request_5cee8c(uint32_t host,uint32_t session) {
    uint32_t payload[2]={0u,0u};
    audio_uart_buffer_zero(payload,8u,0u);
    payload[0]=session;
    payload[1]=host;
    uint32_t magic=(uint32_t)audio_terminal_message_sequence+1u;
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0xdbu,message,magic,host,session);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0cc00000u,short_message,short_message,magic,host,session);
    return audio_terminal_send_message_5ce7c4(0xa5u,0x12u,payload,(uint8_t)magic,1u);
}
