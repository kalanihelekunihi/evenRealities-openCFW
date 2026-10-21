/* Terminal agent-interrupt packet encoder, stock 0x5cee08..0x5cee8b. */
#include <stdint.h>

extern uint8_t audio_terminal_message_sequence; /* stock 0x20074fff */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern uint32_t audio_terminal_send_message_5ce7c4(uint32_t,uint32_t,const void *,uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="pb.terminal";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_terminal\\pb_service_terminal.c";
static const char function[]="APP_PbTerminalTxEncodeAgentInterrupt";
static const char message[]="terminal agent interrupt: magic=%d";
static const char short_message[]="[pb.terminal]terminal agent interrupt: magic=%d";

uint32_t audio_terminal_agent_interrupt_encode_5cee08(void) {
    uint8_t payload=0u;
    audio_uart_buffer_zero(&payload,1u,0u);
    payload=0u;
    uint32_t magic=(uint32_t)audio_terminal_message_sequence+1u;
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0xcbu,message,magic);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c400000u,short_message,short_message,magic);
    return audio_terminal_send_message_5ce7c4(0xa4u,0xcu,&payload,(uint8_t)magic,1u);
}
