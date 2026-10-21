/* Terminal FSM session-list selection, stock 0x5ed4f8..0x5ed742. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern uint32_t audio_terminal_session_command_5eca3e(uint32_t);
extern int32_t audio_terminal_session_index_i16_5eca44(uint32_t);
extern uint8_t *audio_td_active_session(void);
extern uint32_t audio_terminal_session_valid_5eca64(int32_t);
extern void audio_terminal_session_switch_event_5ed1ec(uint32_t);
extern void audio_terminal_ui_stop_service_a_5eceb2(void);
extern void audio_terminal_session_root_hide_5ed1d6(void);
extern uint32_t audio_terminal_request_display(uint8_t,uint32_t);
extern uint32_t audio_terminal_session_switch_request_5cee8c(uint32_t,uint32_t);
extern void audio_uart_page_43ded4(void *,uint32_t);
extern void audio_terminal_session_pending_prompt_5ece4c(const char *);
extern uint8_t audio_td_has_active_session(void);
extern uint32_t audio_td_host_counter_get_5973d4(void);
extern uint32_t audio_terminal_new_session_request_5cef14(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.ui";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_session_list_ui.c";
static const char function[]="terminal_ui_action_session_list_select";
static const char current[]="session select current: idx=%d status=%d";
static const char current_short[]="[terminal.ui]session select current: idx=%d status=%d";
static const char switch_request[]="session switch requested: idx=%d session=%lu";
static const char switch_short[]="[terminal.ui]session switch requested: idx=%d session=%lu";
static const char new_request[]="new session requested: host=%lu";
static const char new_short[]="[terminal.ui]new session requested: host=%lu";
static const char ignored[]="session select ignored: action=%d idx=%d";
static const char ignored_short[]="[terminal.ui]session select ignored: action=%d idx=%d";

static uint32_t load_word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void mark_pending(void) {
    audio_terminal_ui_state_base[0x27eu]=1u;
    uint32_t root=load_word(audio_terminal_ui_state_base+4u);
    if (root!=0u) audio_uart_page_43ded4((void *)(uintptr_t)root,1u);
    audio_terminal_session_pending_prompt_5ece4c(" ");
}

uint32_t audio_terminal_ui_action_5ed4f8(uint32_t old_state,uint32_t payload) {
    (void)old_state;
    uint32_t command=audio_terminal_session_command_5eca3e(payload);
    int32_t index=audio_terminal_session_index_i16_5eca44(payload);
    uint8_t *active=audio_td_active_session();
    switch ((uint8_t)command) {
    case 1u:
        if (active!=0 && audio_terminal_session_valid_5eca64((int16_t)index)!=0u) {
            const uint8_t *record=active+(int16_t)index*0x90;
            uint32_t session=load_word(record+0x9cu);
            uint32_t status=record[0x122u];
            audio_terminal_session_switch_event_5ed1ec(session);
            audio_terminal_ui_stop_service_a_5eceb2();
            audio_terminal_session_root_hide_5ed1d6();
            (void)audio_terminal_request_display(34u,(uint8_t)status);
            if ((audio_log_flags()&2u)!=0u)
                audio_log_extended(3u,module,path,function,0x20fu,current,
                                   (uint32_t)(int16_t)index,status);
            if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x0c800000u,current_short,current_short,
                                            (uint32_t)(int16_t)index,status);
        }
        break;
    case 2u:
        if (active!=0 && audio_terminal_session_valid_5eca64((int16_t)index)!=0u) {
            const uint8_t *record=active+(int16_t)index*0x90;
            uint32_t session=load_word(record+0x9cu);
            (void)audio_terminal_session_switch_request_5cee8c(
                load_word(active),session);
            mark_pending();
            if ((audio_log_flags()&2u)!=0u)
                audio_log_extended(3u,module,path,function,0x21bu,switch_request,
                                   (uint32_t)(int16_t)index,session);
            if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x0c800000u,switch_short,switch_short,
                                            (uint32_t)(int16_t)index,session);
        }
        break;
    case 3u:
        if (audio_td_has_active_session()!=0u) {
            (void)audio_terminal_new_session_request_5cef14(
                audio_td_host_counter_get_5973d4());
            mark_pending();
            if ((audio_log_flags()&2u)!=0u)
                audio_log_extended(3u,module,path,function,0x227u,new_request,
                                   audio_td_host_counter_get_5973d4());
            if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x0c400000u,new_short,new_short,
                                            audio_td_host_counter_get_5973d4());
        }
        break;
    default:
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x22cu,ignored,
                               (uint8_t)command,(uint32_t)(int16_t)index);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08800000u,ignored_short,ignored_short,
                                        (uint8_t)command,(uint32_t)(int16_t)index);
        break;
    }
    return 0u;
}
