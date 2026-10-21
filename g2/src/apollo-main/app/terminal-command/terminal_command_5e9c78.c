/* Apollo terminal_action_session_list, native 0x5e9c78. */
#include <stdint.h>

extern uint32_t audio_td_counter_b_get(void);
extern uint8_t audio_td_flag_b_get(void);
extern uint32_t audio_td_state_sync(const void *);
extern uint8_t *audio_td_state_ptr_alias1(void);
extern uint8_t audio_ux_get_system_ble_status(void);
extern uint8_t audio_td_has_active_session(void);
extern uint8_t audio_terminal_state_is_processing(uint32_t);
extern uint8_t audio_terminal_ui_mode;
extern uint32_t audio_td_bind_temp_session_response_timer(uint32_t);
extern void audio_terminal_apply_session_id_changed(uint32_t,uint8_t);
extern uint8_t audio_terminal_refresh_session_list_if_visible(void);
extern uint16_t audio_td_current_session_index(void);
extern uint32_t audio_terminal_request_display(uint8_t,uint32_t);
extern void audio_terminal_log_session_list_items(const void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_action_session_list";
static const char changed[]="recv terminal session list: host=%lu current=%lu count=%u current_changed=1 new_session_bound=%d restore_current=0";
static const char changed_short[]="[terminal.pb]recv terminal session list: host=%lu current=%lu count=%u current_changed=1 new_session_bound=%d restore_current=0";
static const char stable[]="recv terminal session list: host=%lu current=%lu count=%u current_changed=0 show_selector=%d update_selector=%d";
static const char stable_short[]="[terminal.pb]recv terminal session list: host=%lu current=%lu count=%u current_changed=0 show_selector=%d update_selector=%d";

static uint16_t load_u16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8));
}
static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

uint32_t audio_terminal_command_5e9c78(const void *payload,uint32_t length) {
    (void)length;
    if(payload==0) return UINT32_MAX;
    const uint8_t *p=payload;
    uint32_t previous=audio_td_counter_b_get();
    uint8_t previous_flag=audio_td_flag_b_get();
    (void)audio_td_state_sync(payload);
    uint32_t current=audio_td_counter_b_get();
    uint8_t *state=audio_td_state_ptr_alias1();
    uint8_t ble=audio_ux_get_system_ble_status();
    uint8_t connected=(uint8_t)(ble!=0u && state!=0 && state[0xa1d8u]==2u);
    uint8_t bound=(uint8_t)(current!=0u);
    uint8_t changed_bound=(uint8_t)(previous!=current && previous_flag!=0u);
    uint8_t may_show=0u;
    if(connected && audio_td_has_active_session()!=0u)
        may_show=audio_terminal_state_is_processing(audio_terminal_ui_mode)!=0u;
    uint32_t host=load_u32(p);
    uint32_t listed_current=load_u32(p+4u);
    uint32_t count=load_u16(p+8u);
    if(bound!=0u && previous!=current) {
        if(changed_bound!=0u) (void)audio_td_bind_temp_session_response_timer(current);
        audio_terminal_apply_session_id_changed(current,1u);
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,722u,changed,
                               host,listed_current,count,changed_bound);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0d000000u,changed_short,changed_short,
                                        host,listed_current,count,changed_bound);
        audio_terminal_log_session_list_items(payload);
        return 0u;
    }
    uint8_t show_selector=0u;
    uint8_t update_selector=0u;
    if(may_show!=0u && bound==0u) {
        (void)audio_terminal_request_display(27u,audio_td_current_session_index());
        show_selector=1u;
    } else {
        update_selector=audio_terminal_refresh_session_list_if_visible();
    }
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,736u,stable,
                           host,listed_current,count,show_selector,update_selector!=0u);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0d400000u,stable_short,stable_short,
                                    host,listed_current,count,show_selector,update_selector!=0u);
    audio_terminal_log_session_list_items(payload);
    return 0u;
}
