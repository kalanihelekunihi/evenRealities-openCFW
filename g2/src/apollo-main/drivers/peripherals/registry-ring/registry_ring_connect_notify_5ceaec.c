/* Apollo APP_PbTerminalTxEncodeCommResp 0x5ceaec. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint32_t audio_terminal_send_message_5ce7c4(uint32_t,uint32_t,const void *,
                                                     uint32_t,uint32_t);

static const char module[]="pb.terminal";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_terminal\\pb_service_terminal.c";
static const char function[]="APP_PbTerminalTxEncodeCommResp";
static const char null_message[]="terminal comm resp is null";
static const char null_short[]="[pb.terminal]terminal comm resp is null";
static const char response_message[]="terminal comm resp: magic=%d err_code=%d";
static const char response_short[]="[pb.terminal]terminal comm resp: magic=%d err_code=%d";

uint32_t audio_registry_ring_connect_notify_5ceaec(uint8_t *state,uint32_t sequence) {
    if(state==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,138u,null_message);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,null_short,null_short);
        return 6u;
    }
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,141u,response_message,
                           (uint32_t)sequence,(uint32_t)state[0]);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c800000u,response_short,response_short,
                                    (uint32_t)sequence,(uint32_t)state[0]);
    return audio_terminal_send_message_5ce7c4(0xf0u,13u,state,
                                                (uint32_t)(uint8_t)sequence,0u);
}
