/* Apollo terminal_message_session_matches, native 0x5e818a. */
#include <stdint.h>
extern uint32_t audio_td_counter_b_get(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_message_session_matches";
static const char fallback[]="message";
static const char stale[]="ignore terminal %s for stale session: msg=%lu current=%lu";
static const char stale_short[]="[terminal.pb]ignore terminal %s for stale session: msg=%lu current=%lu";

/* Stock 0x5E818A (terminal_message_session_matches) */
uint32_t audio_terminal_message_session_matches(uint32_t session,const char *kind) {
    uint32_t current=audio_td_counter_b_get();
    if(session==current) return 1u;
    const char *label=kind!=0 ? kind : fallback;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(2u,module,path,function,45u,stale,
                           label,session,current);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x08c00000u,stale_short,stale_short,
                                    label,session,current);
    return 0u;
}
