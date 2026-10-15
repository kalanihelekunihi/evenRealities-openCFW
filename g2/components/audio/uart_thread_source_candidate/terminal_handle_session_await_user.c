/* Apollo terminal_handle_session_await_user, native 0x5e84a8. */
#include <stdint.h>
extern uint8_t audio_terminal_ui_mode;
extern uint32_t audio_terminal_display_queue_handle;
extern uint32_t audio_terminal_runtime_saved_session;
extern uint8_t audio_terminal_runtime_flag_277;
extern uint8_t audio_terminal_runtime_flag_27f;
extern uint32_t audio_td_counter_b_get(void);
extern void audio_td_dismiss_query_notification(uint32_t);
extern uint8_t audio_td_session_marked(uint32_t);
extern uint8_t audio_terminal_refresh_session_list_if_visible(void);
extern uint8_t audio_uart_device_role_get(void);
extern uint32_t audio_system_alert_command_45a8ee(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint8_t audio_terminal_state_allows_runtime_event(uint32_t);
extern uint32_t audio_terminal_request_display(uint8_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_handle_session_await_user";
static const char no_session[]="drop await-user notification without session id";
static const char no_session_short[]="[terminal.pb]drop await-user notification without session id";
static const char processing[]="drop current-session await-user while agent processing: session=%lu";
static const char processing_short[]="[terminal.pb]drop current-session await-user while agent processing: session=%lu";
static const char list_refresh[]="dismiss await-user in session list and refresh: session=%lu";
static const char list_refresh_short[]="[terminal.pb]dismiss await-user in session list and refresh: session=%lu";
static const char list_no_refresh[]="dismiss await-user in session list without refresh: session=%lu";
static const char list_no_refresh_short[]="[terminal.pb]dismiss await-user in session list without refresh: session=%lu";
static const char dismissed[]="drop dismissed await-user notification: session=%lu";
static const char dismissed_short[]="[terminal.pb]drop dismissed await-user notification: session=%lu";
static const char startup[]="await-user received while display off, startup notification: session=%lu";
static const char startup_short[]="[terminal.pb]await-user received while display off, startup notification: session=%lu";
static const char dropped[]="drop await-user notification in state=%d session=%lu";
static const char dropped_short[]="[terminal.pb]drop await-user notification in state=%d session=%lu";

void audio_terminal_handle_session_await_user(uint32_t session) {
    uint8_t mode=audio_terminal_ui_mode;
    if(session==0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,170u,no_session);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08000000u,no_session_short,no_session_short);
        return;
    }
    uint32_t current=audio_td_counter_b_get();
    if(session==current && mode==7u) {
        audio_td_dismiss_query_notification(session);
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,175u,processing,session);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c400000u,processing_short,processing_short,session);
        return;
    }
    if(mode==11u) {
        audio_td_dismiss_query_notification(session);
        if(audio_terminal_refresh_session_list_if_visible()!=0u) {
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(3u,module,path,function,181u,list_refresh,session);
            if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x0c400000u,list_refresh_short,list_refresh_short,session);
        } else {
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(3u,module,path,function,183u,list_no_refresh,session);
            if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x0c400000u,list_no_refresh_short,list_no_refresh_short,session);
        }
        return;
    }
    if(audio_td_session_marked(session)!=0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,188u,dismissed,session);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c400000u,dismissed_short,dismissed_short,session);
        return;
    }
    if(mode==0u || audio_terminal_display_queue_handle==0u) {
        audio_terminal_runtime_saved_session=session;
        audio_terminal_runtime_flag_277=0u;
        audio_terminal_runtime_flag_27f=0u;
        if(audio_uart_device_role_get()==1u)
            (void)audio_system_alert_command_45a8ee(48u,0u,0u,0u);
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,198u,startup,session);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c400000u,startup_short,startup_short,session);
        return;
    }
    if(audio_terminal_state_allows_runtime_event(mode)!=0u) {
        (void)audio_terminal_request_display(22u,session);
        return;
    }
    audio_td_dismiss_query_notification(session);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(2u,module,path,function,208u,dropped,mode,session);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x08800000u,dropped_short,dropped_short,mode,session);
}
