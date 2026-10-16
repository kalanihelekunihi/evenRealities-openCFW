/* Terminal FSM session-status action, stock 0x5e6018..0x5e6253. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern uint8_t audio_terminal_output_style_20003f80[];
extern uint32_t audio_terminal_counter_b_get_5973dc(void);
extern uint32_t audio_td_record_status_for_session(uint32_t);
extern void audio_terminal_ui_stop_service_c_5ebbc6(void);
extern void audio_td_session_struct_clear(void);
extern void audio_uart_page_43dfa4(void *,uint32_t);
extern void audio_terminal_processing_prepare_5ea30c(void);
extern uint32_t audio_terminal_set_label_style_5e482a(uint32_t,const void *,uint32_t,uint32_t);
extern const char *audio_uart_page_49942e(uint8_t *,const char *);
extern void audio_terminal_elapsed_refresh_5e4902(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.ui";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[]="terminal_ui_action_session_status_update";
static const char stale[]="ignore stale session status ui update: msg=%lu current=%lu state=%d";
static const char stale_short[]="[terminal.ui]ignore stale session status ui update: msg=%lu current=%lu state=%d";
static const char status_message[]="session status: %d";
static const char status_short[]="[terminal.ui]session status: %d";
static const char ignored[]="ignore session status in query pending: %d";
static const char ignored_short[]="[terminal.ui]ignore session status in query pending: %d";
static const char waiting[]="Thinking...";
static const char hint[]="[Tap & hold to stop response]";

static uint32_t word(uint32_t offset) {
    const uint8_t *p=audio_terminal_ui_state_base+offset;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void show_waiting(void) {
    uint32_t icon=word(0x1ccu),title=word(0x1d0u);
    uint32_t label=word(0x1d4u),sub=word(0x1dcu);
    if (icon!=0u && title!=0u && label!=0u && sub!=0u) {
        audio_uart_page_43dfa4((void *)(uintptr_t)icon,1u);
        audio_terminal_processing_prepare_5ea30c();
        (void)audio_terminal_set_label_style_5e482a(
            title,audio_terminal_output_style_20003f80,6u,100u);
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)label,waiting);
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)sub,hint);
        audio_terminal_elapsed_refresh_5e4902();
    }
}
static void log_status(uint8_t status,uint32_t line) {
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,line,status_message,(uint32_t)status);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c400000u,status_short,status_short,(uint32_t)status);
}

uint32_t audio_terminal_ui_action_5e6018(uint32_t old_state,uint32_t session) {
    uint32_t current=audio_terminal_counter_b_get_5973dc();
    if (session==0u || session!=current) {
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x532u,stale,
                               session,current,(uint32_t)(uint8_t)old_state);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08c00000u,stale_short,stale_short,
                                        session,current,(uint32_t)(uint8_t)old_state);
        return (uint32_t)(uint8_t)old_state+1u;
    }
    uint32_t status=(uint32_t)audio_td_record_status_for_session(session)&0xffu;
    if ((uint8_t)old_state==9u) {
        if (status==1u) {
            audio_terminal_ui_stop_service_c_5ebbc6();
            audio_td_session_struct_clear();
            show_waiting();
            log_status(status,0x544u);
            return 8u;
        }
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x547u,ignored,(uint32_t)status);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08400000u,ignored_short,ignored_short,(uint32_t)status);
        return 10u;
    }
    show_waiting();
    log_status(status,0x553u);
    return 0u;
}
