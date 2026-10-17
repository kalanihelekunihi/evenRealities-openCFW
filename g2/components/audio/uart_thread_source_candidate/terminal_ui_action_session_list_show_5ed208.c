/* Terminal FSM session-list-show action, stock 0x5ed208..0x5ed317. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern int32_t audio_terminal_session_index_i16_5eca44(uint32_t);
extern uint8_t audio_td_flag_b_get(void);
extern void audio_terminal_cancel_pending_5cef8c(void);
extern void audio_td_flag_b_set_597572(uint32_t);
extern void audio_terminal_ui_stop_service_b_5ec268(void);
extern void audio_terminal_ui_stop_service_c_5ebbc6(void);
extern void audio_terminal_ui_stop_service_e_5ec9c0(void);
extern void audio_terminal_ui_stop_service_d_5ec770(void);
extern void audio_uart_page_43ded4(void *,uint32_t);
extern void audio_terminal_session_list_event_5ed1fa(void);
extern void audio_terminal_session_list_rebuild_5ecef6(int32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.ui";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_session_list_ui.c";
static const char function[]="terminal_ui_action_session_list_show";
static const char cancelled[]="new session pending cancelled before selector reopen";
static const char cancelled_short[]="[terminal.ui]new session pending cancelled before selector reopen";
static const char shown[]="session list show: from=%d selected=%d";
static const char shown_short[]="[terminal.ui]session list show: from=%d selected=%d";

static uint32_t word(uint32_t offset) {
    const uint8_t *p=audio_terminal_ui_state_base+offset;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

uint32_t audio_terminal_ui_action_5ed208(uint32_t old_state,uint32_t payload) {
    int32_t selected=audio_terminal_session_index_i16_5eca44(payload);
    audio_terminal_ui_state_base[0x276u]=(uint8_t)old_state==12u ? 2u : (uint8_t)old_state;
    if ((uint8_t)old_state==12u && audio_td_flag_b_get()!=0u) {
        audio_terminal_cancel_pending_5cef8c();
        audio_td_flag_b_set_597572(0u);
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,0x1c1u,cancelled);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c000000u,cancelled_short,cancelled_short);
    }
    audio_terminal_ui_stop_service_b_5ec268();
    audio_terminal_ui_stop_service_c_5ebbc6();
    audio_terminal_ui_stop_service_e_5ec9c0();
    if ((uint8_t)old_state!=8u) audio_terminal_ui_stop_service_d_5ec770();
    uint32_t root=word(0u);
    if (root!=0u) audio_uart_page_43ded4((void *)(uintptr_t)root,1u);
    audio_terminal_session_list_event_5ed1fa();
    audio_terminal_session_list_rebuild_5ecef6((int16_t)selected);
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x1d0u,shown,
                           (uint32_t)(uint8_t)old_state,(uint32_t)(int16_t)selected);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c800000u,shown_short,shown_short,
                                    (uint32_t)(uint8_t)old_state,(uint32_t)(int16_t)selected);
    return 0u;
}
