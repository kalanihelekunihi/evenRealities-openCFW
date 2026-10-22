/* Apollo terminal_refresh_session_list_if_visible, native 0x5e8208. */
#include <stdint.h>
extern uint8_t audio_terminal_ui_mode; /* native RAM 0x2006e345 */
extern uint8_t audio_terminal_selector_loading; /* native RAM 0x2006e34d, state-base +0x27d */
extern uint32_t audio_terminal_request_display(uint8_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_refresh_session_list_if_visible";
static const char loading[]="session list is loading, skip refresh";
static const char loading_short[]="[terminal.pb]session list is loading, skip refresh";

/* Stock 0x5E8208 (terminal_refresh_session_list_if_visible) */
uint8_t audio_terminal_refresh_session_list_if_visible(void) {
    if(audio_terminal_ui_mode!=11u) return 0u;
    if(audio_terminal_selector_loading!=0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,55u,loading);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08000000u,loading_short,loading_short);
        return 0u;
    }
    (void)audio_terminal_request_display(28u,0x40000000u);
    return 1u;
}
