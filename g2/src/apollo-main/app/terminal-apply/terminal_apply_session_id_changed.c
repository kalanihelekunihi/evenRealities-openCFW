/* Apollo terminal_apply_session_id_changed, native 0x5e8346. */
#include <stdint.h>

extern void audio_td_session_bind_store(uint32_t);
extern uint8_t audio_terminal_cached_session_status(uint32_t);
extern void audio_td_flag_set_with_reset(uint8_t);
extern void audio_terminal_reset_output_tracking(void);
extern void audio_td_ring_reset_wrapper(void);
extern void audio_td_notify_state_clear(void);
extern void audio_td_session_struct_clear(void);
extern void audio_td_record_status_set(uint32_t,uint8_t);
extern uint8_t audio_td_has_active_session(void);
extern uint16_t audio_td_current_session_index(void);
extern uint32_t audio_terminal_request_display(uint8_t,uint32_t);
extern const char *audio_terminal_session_status_name(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

/* Native RAM 0x2006e345; final linker placement remains open. */
extern uint8_t audio_terminal_ui_mode; /* state-base +0x275 */

static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_apply_session_id_changed";
static const char update[]="recv terminal session id changed to none, update selector";
static const char update_short[]="[terminal.pb]recv terminal session id changed to none, update selector";
static const char show[]="recv terminal session id changed to none, show selector";
static const char show_short[]="[terminal.pb]recv terminal session id changed to none, show selector";
static const char changed[]="recv terminal session id changed: session=%lu status=%d(%s)";
static const char changed_short[]="[terminal.pb]recv terminal session id changed: session=%lu status=%d(%s)";

void audio_terminal_apply_session_id_changed(uint32_t session,uint8_t reset_ring) {
    audio_td_session_bind_store(session);
    uint8_t status=audio_terminal_cached_session_status(session);
    audio_td_flag_set_with_reset(0u);
    audio_terminal_reset_output_tracking();
    if(reset_ring!=0u) audio_td_ring_reset_wrapper();
    audio_td_notify_state_clear();
    audio_td_session_struct_clear();
    audio_td_record_status_set(session,status);
    if(session==0u && audio_td_has_active_session()!=0u) {
        if(audio_terminal_ui_mode==11u) {
            (void)audio_terminal_request_display(28u,0x40000000u);
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(3u,module,path,function,153u,update);
            if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x0c000000u,update_short,update_short);
        } else {
            uint16_t index=audio_td_current_session_index();
            (void)audio_terminal_request_display(27u,index);
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(3u,module,path,function,156u,show);
            if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x0c000000u,show_short,show_short);
        }
    } else {
        (void)audio_terminal_request_display(35u,session);
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,162u,changed,
                               session,status,audio_terminal_session_status_name(status));
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0cc00000u,changed_short,changed_short,
                                        session,status,audio_terminal_session_status_name(status));
    }
}
