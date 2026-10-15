/* Apollo terminal_action_session_id_changed, native 0x5e9f74. */
#include <stdint.h>

extern uint32_t g2_flashdb_candidate_tick(void);
extern void audio_terminal_apply_session_id_changed(uint32_t,uint8_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

/* Native RAM 0x2006e36c; final linker placement remains open. */
uint32_t audio_terminal_session_switch_tick;
static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_action_session_id_changed";
static const char message[]="block input during session switch content sync: session=%lu tick=%lu";
static const char short_message[]="[terminal.pb]block input during session switch content sync: session=%lu tick=%lu";

uint32_t audio_terminal_command_5e9f74(const void *payload,uint32_t length) {
    (void)length;
    if(payload==0) return UINT32_MAX;
    uint32_t session=*(const uint32_t *)payload;
    if(session!=0u) {
        uint32_t tick=g2_flashdb_candidate_tick();
        audio_terminal_session_switch_tick=tick==0u?1u:tick;
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,795u,message,
                               session,audio_terminal_session_switch_tick);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c800000u,short_message,short_message,
                                        session,audio_terminal_session_switch_tick);
    } else {
        audio_terminal_session_switch_tick=0;
    }
    audio_terminal_apply_session_id_changed(session,1u);
    return 0;
}
