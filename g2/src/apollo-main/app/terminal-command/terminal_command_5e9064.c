/* Apollo terminal_action_session_status, native 0x5e9064. */
#include <stdint.h>
extern uint8_t audio_terminal_ui_mode; /* native RAM 0x2006e345 */
extern uint32_t audio_terminal_runtime_saved_session; /* native RAM 0x2006e358 */
struct audio_terminal_output_tracking {
    uint8_t active;
    uint8_t reserved[3];
    uint32_t count;
};
extern struct audio_terminal_output_tracking audio_terminal_output_tracking;
extern uint32_t audio_terminal_session_switch_tick; /* native RAM 0x2006e36c */
extern uint32_t audio_terminal_message_session_matches(uint32_t,const char *);
extern const char *audio_terminal_session_status_name(uint32_t);
extern void audio_td_record_status_set(uint32_t,uint8_t);
extern void audio_terminal_handle_session_await_user(uint32_t);
extern uint32_t audio_td_counter_b_get(void);
extern void audio_terminal_reset_output_tracking(void);
extern void audio_td_record_timer_clear(uint32_t);
extern void audio_td_ring_reset_wrapper(void);
extern void audio_td_notify_state_clear(void);
extern void audio_td_session_struct_clear(void);
extern uint8_t audio_terminal_refresh_session_list_if_visible(void);
extern uint32_t audio_terminal_request_display(uint8_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_action_session_status";
static const char received[]="recv terminal session status:id=%lu,status=%d(%s)";
static const char received_short[]="[terminal.pb]recv terminal session status:id=%lu,status=%d(%s)";
static const char sync_end[]="session sync end";
static const char unblocked[]="session history sync end, unblock input: session=%lu";
static const char unblocked_short[]="[terminal.pb]session history sync end, unblock input: session=%lu";
static const char dismiss[]="dismiss query notification by thinking status: session=%lu";
static const char dismiss_short[]="[terminal.pb]dismiss query notification by thinking status: session=%lu";
static const char cached[]="session status cached for inactive session: session=%lu status=%d(%s)";
static const char cached_short[]="[terminal.pb]session status cached for inactive session: session=%lu status=%d(%s)";
static const char skipped[]="skip session status ui refresh during output interval: status=%d(%s)";
static const char skipped_short[]="[terminal.pb]skip session status ui refresh during output interval: status=%d(%s)";

static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

uint32_t audio_terminal_command_5e9064(const void *payload,uint32_t length) {
    (void)length;
    if(payload==0) return UINT32_MAX;
    const uint8_t *p=payload;
    uint8_t status=p[0];
    uint32_t session=load_u32(p+4u);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,436u,received,
                           session,status,audio_terminal_session_status_name(status));
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0cc00000u,received_short,received_short,
                                    session,status,audio_terminal_session_status_name(status));
    if(status==5u) {
        if(audio_terminal_message_session_matches(session,sync_end)!=0u) {
            audio_terminal_session_switch_tick=0u;
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(3u,module,path,function,442u,unblocked,session);
            if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x0c400000u,unblocked_short,unblocked_short,session);
        }
        return 0u;
    }
    audio_td_record_status_set(session,status);
    if(status==2u) {
        audio_terminal_handle_session_await_user(session);
        return 0u;
    }
    if(status==1u && audio_terminal_ui_mode==10u &&
       audio_terminal_runtime_saved_session==session) {
        (void)audio_terminal_request_display(24u,1u);
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,457u,dismiss,session);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c400000u,dismiss_short,dismiss_short,session);
    }
    if(session!=audio_td_counter_b_get()) {
        (void)audio_terminal_refresh_session_list_if_visible();
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,464u,cached,
                               session,status,audio_terminal_session_status_name(status));
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08c00000u,cached_short,cached_short,
                                        session,status,audio_terminal_session_status_name(status));
        return 0u;
    }
    if(status==1u && audio_terminal_output_tracking.active!=0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(4u,module,path,function,492u,skipped,
                               status,audio_terminal_session_status_name(status));
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x10800000u,skipped_short,skipped_short,
                                        status,audio_terminal_session_status_name(status));
        return 0u;
    }
    if(status==3u || status==4u) {
        audio_terminal_reset_output_tracking();
        audio_td_record_timer_clear(session);
        if(status==4u) audio_td_ring_reset_wrapper();
        audio_td_notify_state_clear();
        audio_td_session_struct_clear();
        if(audio_terminal_refresh_session_list_if_visible()==0u)
            (void)audio_terminal_request_display(status==3u?16u:17u,0u);
        return 0u;
    }
    if(audio_terminal_refresh_session_list_if_visible()==0u)
        (void)audio_terminal_request_display(15u,session);
    return 0u;
}
