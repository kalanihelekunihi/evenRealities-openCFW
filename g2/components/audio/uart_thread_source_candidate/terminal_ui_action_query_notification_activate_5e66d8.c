/* Terminal query-notification activation action, stock 0x5e66d8..0x5e68ad. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern uint32_t audio_terminal_counter_b_get_5973dc(void);
extern uint8_t *audio_td_active_session(void);
extern uint32_t audio_td_host_counter_get_5973d4(void);
extern void audio_td_dismiss_query_notification(uint32_t);
extern int32_t audio_terminal_ui_restore_query_5e6620(uint32_t);
extern void audio_terminal_ui_stop_service_e_5ec9c0(void);
extern int32_t audio_terminal_ui_action_5e583c(uint32_t,uint32_t);
extern void audio_terminal_ui_event_5e5484(uint32_t,uint32_t,uint32_t);
extern void audio_terminal_reset_ancillary_5e65f8(void);
extern uint32_t audio_terminal_session_switch_request_5cee8c(uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.ui";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[]="terminal_ui_action_query_notification_activate";
static const char none[]="query notification activate ignored: no target session";
static const char none_short[]="[terminal.ui]query notification activate ignored: no target session";
static const char current[]="query notification activate current session=%lu";
static const char current_short[]="[terminal.ui]query notification activate current session=%lu";
static const char failed[]="query notification activate failed: session=%lu found=%d host=%lu";
static const char failed_short[]="[terminal.ui]query notification activate failed: session=%lu found=%d host=%lu";
static const char switched[]="query notification switch requested: session=%lu";
static const char switched_short[]="[terminal.ui]query notification switch requested: session=%lu";

static uint32_t session_word(void) {
    const uint8_t *p=audio_terminal_ui_state_base+0x288u;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static uint32_t record_session(const uint8_t *record) {
    const uint8_t *p=record+0x9cu;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

int32_t audio_terminal_ui_action_5e66d8(uint32_t old_state,uint32_t payload) {
    (void)payload;
    uint32_t target=session_word();
    uint32_t current_session=audio_terminal_counter_b_get_5973dc();
    uint8_t *active=audio_td_active_session();
    uint32_t host=audio_td_host_counter_get_5973d4();
    if (target==0u) {
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x60fu,none);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08000000u,none_short,none_short);
        return audio_terminal_ui_restore_query_5e6620((uint8_t)old_state);
    }
    audio_td_dismiss_query_notification(target);
    if (target==current_session) {
        audio_terminal_ui_stop_service_e_5ec9c0();
        (void)audio_terminal_ui_action_5e583c((uint8_t)old_state,0u);
        audio_terminal_ui_event_5e5484(4u,target,0u);
        audio_terminal_reset_ancillary_5e65f8();
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,0x619u,current,target);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c400000u,current_short,current_short,target);
        return 8;
    }
    uint32_t found=0u;
    if (active!=0u) {
        uint32_t count=(uint32_t)active[8]|((uint32_t)active[9]<<8)|
                       ((uint32_t)active[10]<<16)|((uint32_t)active[11]<<24);
        for (uint32_t i=0u;i<count;i++) {
            if (record_session(active+i*0x90u)==target) {
                found=1u;
                break;
            }
        }
    }
    if (found==0u || host==0u) {
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x627u,failed,target,found,host);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08c00000u,failed_short,failed_short,
                                        target,found,host);
        return audio_terminal_ui_restore_query_5e6620((uint8_t)old_state);
    }
    audio_terminal_ui_state_base[0x27fu]=1u;
    (void)audio_terminal_session_switch_request_5cee8c(host,target);
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x62du,switched,target);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c400000u,switched_short,switched_short,target);
    return 0;
}
