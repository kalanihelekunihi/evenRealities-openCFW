/* Terminal new-session request packet encoder, stock 0x5cef14..0x5cef8a. */
#include <stdint.h>

extern uint8_t audio_terminal_message_sequence;
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern uint32_t audio_terminal_send_message_5ce7c4(uint32_t,uint32_t,const void *,uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="pb.terminal";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_terminal\\pb_service_terminal.c";
static const char function[]="APP_PbTerminalTxEncodeNewSessionRequest";
static const char message[]="terminal new session request: magic=%d host=%lu";
static const char short_message[]="[pb.terminal]terminal new session request: magic=%d host=%lu";

uint32_t audio_terminal_new_session_request_5cef14(uint32_t host) {
    uint32_t payload=0u;
    audio_uart_buffer_zero(&payload,4u,0u);
    payload=host;
    uint32_t magic=(uint32_t)audio_terminal_message_sequence+1u;
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0xe9u,message,magic,host);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c800000u,short_message,short_message,magic,host);
    return audio_terminal_send_message_5ce7c4(0xa6u,0x13u,&payload,(uint8_t)magic,1u);
}
