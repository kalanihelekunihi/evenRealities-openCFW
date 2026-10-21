/* Terminal FSM new-session failure, stock 0x5ed8e0..0x5ed9ba. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern void audio_uart_page_43dfa4(void *,uint32_t);
extern void audio_terminal_session_list_rebuild_5ecef6(int32_t);
extern void audio_terminal_ui_stop_service_b_5ec268(void);
extern void audio_terminal_ui_stop_service_c_5ebbc6(void);
extern void audio_terminal_ui_stop_service_d_5ec770(void);
extern int32_t audio_td_current_session_index_signed(void);
extern uint32_t audio_terminal_request_display(uint8_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.ui";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_session_list_ui.c";
static const char function[]="terminal_ui_action_new_session_result_failed";
static const char denied[]="new session denied, keep selector";
static const char denied_short[]="[terminal.ui]new session denied, keep selector";
static const char failed[]="new session failed after pending prompt, reopen selector";
static const char failed_short[]="[terminal.ui]new session failed after pending prompt, reopen selector";

static uint32_t word(uint32_t offset) {
    const uint8_t *p=audio_terminal_ui_state_base+offset;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

uint32_t audio_terminal_ui_action_5ed8e0(uint32_t old_state,uint32_t payload) {
    (void)payload;
    if ((uint8_t)old_state==11u) {
        audio_terminal_ui_state_base[0x27du]=0u;
        audio_terminal_ui_state_base[0x27eu]=0u;
        uint32_t root=word(4u);
        if (root!=0u) audio_uart_page_43dfa4((void *)(uintptr_t)root,1u);
        int32_t selected=*(const int16_t *)(const void *)(audio_terminal_ui_state_base+0x27au);
        audio_terminal_session_list_rebuild_5ecef6(selected);
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x271u,denied);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08000000u,denied_short,denied_short);
    } else {
        audio_terminal_ui_state_base[0x27eu]=0u;
        uint32_t root=word(4u);
        if (root!=0u) audio_uart_page_43dfa4((void *)(uintptr_t)root,1u);
        audio_terminal_ui_stop_service_b_5ec268();
        audio_terminal_ui_stop_service_c_5ebbc6();
        audio_terminal_ui_stop_service_d_5ec770();
        uint32_t selected=(uint16_t)(int16_t)audio_td_current_session_index_signed();
        (void)audio_terminal_request_display(27u,selected);
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x27du,failed);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08000000u,failed_short,failed_short);
    }
    return 0u;
}
