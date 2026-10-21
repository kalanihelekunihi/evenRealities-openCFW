/* Terminal query reply FSM action, stock 0x5e69a0..0x5e6b09. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern uint8_t audio_terminal_output_style_20003f80[];
extern uint32_t audio_terminal_output_payload_20074a94;
extern uint8_t audio_terminal_output_active_2007502c;
extern uint8_t audio_terminal_output_mode_2007502d;
extern uint8_t *audio_td_session_struct_ptr(void);
extern void audio_td_session_struct_clear(void);
extern void audio_terminal_reset_display_5e4c84(uint32_t);
extern uint32_t audio_terminal_query_reply_send_5ced38(const uint32_t *);
extern void audio_terminal_ui_stop_service_c_5ebbc6(void);
extern void audio_uart_page_43dfa4(void *,uint32_t);
extern void audio_terminal_processing_prepare_5ea30c(void);
extern uint32_t audio_terminal_set_label_style_5e482a(uint32_t,const void *,uint32_t,uint32_t);
extern uint32_t audio_terminal_select_output_mode_5ea2a8(uint32_t);
extern const char *audio_uart_page_49942e(uint8_t *,const char *);
extern void audio_terminal_elapsed_refresh_5e4902(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.ui";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[]="terminal_ui_action_query_reply";
static const char reply[]="query reply: query_id=%d, option_id=%d, selected_idx=%d";
static const char reply_short[]="[terminal.ui]query reply: query_id=%d, option_id=%d, selected_idx=%d";
static const char thinking[]="Thinking...";
static const char hint[]="[Tap & hold to stop response]";

static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static uint16_t halfword(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8));
}

int32_t audio_terminal_ui_action_5e69a0(uint32_t old_state,uint32_t payload) {
    (void)old_state;
    uint8_t *session=audio_td_session_struct_ptr();
    audio_terminal_ui_state_base[0x28cu]=1u;
    audio_terminal_reset_display_5e4c84(0u);
    uint32_t index=(uint8_t)payload;
    uint32_t output=(payload>>31)&1u;
    uint32_t selected=(payload>>8)&0xffu;
    if (session!=0 && index<halfword(session+0x406u)) {
        uint32_t packet[2]={word(session),word(session+0x408u+index*0x88u)};
        (void)audio_terminal_query_reply_send_5ced38(packet);
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,0x662u,reply,
                               packet[0],packet[1],index);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0cc00000u,reply_short,reply_short,
                                        packet[0],packet[1],index);
    }
    audio_terminal_ui_stop_service_c_5ebbc6();
    audio_td_session_struct_clear();
    uint32_t icon=word(audio_terminal_ui_state_base+0x1ccu);
    uint32_t title=word(audio_terminal_ui_state_base+0x1d0u);
    uint32_t label=word(audio_terminal_ui_state_base+0x1d4u);
    uint32_t sub=word(audio_terminal_ui_state_base+0x1dcu);
    if (icon!=0u && title!=0u && label!=0u && sub!=0u) {
        audio_uart_page_43dfa4((void *)(uintptr_t)icon,1u);
        audio_terminal_processing_prepare_5ea30c();
        (void)audio_terminal_set_label_style_5e482a(
            title,audio_terminal_output_style_20003f80,6u,100u);
        if (output!=0u) {
            (void)audio_terminal_select_output_mode_5ea2a8(selected);
            audio_terminal_output_mode_2007502d=(uint8_t)selected;
            audio_terminal_output_payload_20074a94=selected;
            audio_terminal_output_active_2007502c=1u;
        } else {
            (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)label,thinking);
            audio_terminal_output_active_2007502c=0u;
        }
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)sub,hint);
        audio_terminal_elapsed_refresh_5e4902();
    }
    return 0;
}
