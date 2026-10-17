/* Terminal FSM session-switch result, stock 0x5ed758..0x5ed85a. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern uint32_t audio_terminal_counter_b_get_5973dc(void);
extern uint8_t *audio_td_active_session(void);
extern uint32_t audio_terminal_session_valid_5eca64(int32_t);
extern void audio_terminal_session_switch_event_5ed1ec(uint32_t);
extern void audio_terminal_ui_stop_service_a_5eceb2(void);
extern void audio_terminal_session_root_hide_5ed1d6(void);
extern uint32_t audio_terminal_request_display(uint8_t,uint32_t);
extern void audio_terminal_session_list_rebuild_5ecef6(int32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.ui";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_session_list_ui.c";
static const char function[]="terminal_ui_action_session_switch_result";
static const char success[]="session switch success, close selector: status=%d";
static const char success_short[]="[terminal.ui]session switch success, close selector: status=%d";
static const char failed[]="session switch failed, keep selector";
static const char failed_short[]="[terminal.ui]session switch failed, keep selector";

static int16_t selected_index(void) {
    const uint8_t *p=audio_terminal_ui_state_base+0x27au;
    return (int16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8));
}
static uint32_t load_word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

uint32_t audio_terminal_ui_action_5ed758(uint32_t old_state,uint32_t payload) {
    if ((uint8_t)old_state!=11u) return 0u;
    if ((uint8_t)payload==0u) {
        uint32_t session=audio_terminal_counter_b_get_5973dc();
        uint8_t *active=audio_td_active_session();
        uint32_t status=0u;
        if (active!=0 && audio_terminal_session_valid_5eca64(selected_index())!=0u) {
            const uint8_t *record=active+(int32_t)selected_index()*0x90;
            session=load_word(record+0x9cu);
            status=record[0x122u];
        }
        audio_terminal_session_switch_event_5ed1ec(session);
        audio_terminal_ui_stop_service_a_5eceb2();
        audio_terminal_session_root_hide_5ed1d6();
        (void)audio_terminal_request_display(34u,(uint8_t)status);
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,0x24eu,success,status);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c400000u,success_short,success_short,status);
    } else {
        audio_terminal_ui_state_base[0x27du]=0u;
        audio_terminal_ui_state_base[0x27eu]=0u;
        audio_terminal_session_list_rebuild_5ecef6(selected_index());
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x255u,failed);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08000000u,failed_short,failed_short);
    }
    return 0u;
}
