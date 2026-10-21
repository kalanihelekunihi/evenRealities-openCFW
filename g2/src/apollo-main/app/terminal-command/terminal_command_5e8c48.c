/* Apollo terminal_action_host_status, native 0x5e8c48. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_mode; /* native RAM 0x2006e345 */
extern const char *audio_terminal_host_status_name(uint32_t);
extern uint8_t *audio_td_state_ptr_alias2(void);
extern void audio_td_notify_state_clear(void);
extern void audio_td_session_struct_clear(void);
extern uint8_t audio_td_has_active_session(void);
extern uint32_t audio_td_counter_b_get(void);
extern uint8_t audio_terminal_state_is_processing(uint32_t);
extern void audio_terminal_apply_session_id_changed(uint32_t,uint8_t);
extern uint16_t audio_td_current_session_index(void);
extern uint32_t audio_terminal_request_display(uint8_t,uint32_t);
extern uint8_t audio_ux_get_system_ble_status(void);
extern void audio_terminal_request_runtime_event_if_allowed(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_action_host_status";
static const char received[]="recv terminal host status: host_status=%d(%s)";
static const char received_short[]="[terminal.pb]recv terminal host status: host_status=%d(%s)";
static const char restore[]="host streaming with current session, restore main page: session=%lu";
static const char restore_short[]="[terminal.pb]host streaming with current session, restore main page: session=%lu";
static const char cached[]="host streaming with host id, show cached session list";
static const char cached_short[]="[terminal.pb]host streaming with host id, show cached session list";
static const char no_host[]="host streaming without host id, keep current ui";
static const char no_host_short[]="[terminal.pb]host streaming without host id, keep current ui";

uint32_t audio_terminal_command_5e8c48(const void *payload,uint32_t length) {
    (void)length;
    if(payload==0) return UINT32_MAX;
    uint8_t next=*(const uint8_t *)payload;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,351u,received,
                           next,audio_terminal_host_status_name(next));
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c800000u,received_short,received_short,
                                    next,audio_terminal_host_status_name(next));
    uint8_t *state=audio_td_state_ptr_alias2();
    uint8_t previous=state[0xa1d8u];
    if(previous==next) return 0;
    state[0xa1d8u]=next;
    if((next==0u || next==1u) && previous!=0u && previous!=1u) {
        audio_td_notify_state_clear();
        audio_td_session_struct_clear();
    }
    if(next!=2u) {
        audio_terminal_request_runtime_event_if_allowed(audio_ux_get_system_ble_status());
        return 0;
    }
    if(audio_td_has_active_session()==0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,385u,no_host);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c000000u,no_host_short,no_host_short);
        return 0;
    }
    uint32_t session=audio_td_counter_b_get();
    if(audio_terminal_state_is_processing(audio_terminal_ui_mode)==0u) return 0;
    if(session!=0u) {
        audio_terminal_apply_session_id_changed(session,1u);
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,378u,restore,session);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c400000u,restore_short,restore_short,session);
        return 0;
    }
    uint16_t index=audio_td_current_session_index();
    (void)audio_terminal_request_display(27u,index);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,382u,cached);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c000000u,cached_short,cached_short);
    return 0;
}
