/* Terminal FSM input-confirm action, stock 0x5e5bc6..0x5e5ca1. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern uint8_t audio_terminal_output_style_20003f80[];
extern uint32_t audio_terminal_counter_b_get_5973dc(void);
extern void audio_td_session_activate_597596(uint32_t);
extern void audio_td_record_status_set_current_597452(uint32_t);
extern void audio_terminal_ui_stop_service_b_5ec268(void);
extern void audio_terminal_reset_display_5e4c84(uint32_t);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void audio_terminal_encode_voice_input_5cec72(const uint8_t *);
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
static const char function[]="terminal_ui_action_input_confirm";
static const char message[]="input confirmed, entering agent processing";
static const char short_message[]="[terminal.ui]input confirmed, entering agent processing";
static const char thinking[]="Thinking...";
static const char stop_hint[]="[Tap & hold to stop response]";
static uint32_t word(uint32_t offset) {
    const uint8_t *p=audio_terminal_ui_state_base+offset;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

uint32_t audio_terminal_ui_action_5e5bc6(uint32_t old_state,uint32_t event_payload) {
    (void)old_state;(void)event_payload;
    uint32_t session=audio_terminal_counter_b_get_5973dc();
    audio_td_session_activate_597596(session);
    audio_td_record_status_set_current_597452(1u);
    audio_terminal_ui_stop_service_b_5ec268();
    audio_terminal_ui_state_base[0x28cu]=1u;
    audio_terminal_reset_display_5e4c84(0u);
    uint8_t packet=0u;
    audio_uart_buffer_zero(&packet,1u,0u);
    packet=4u;
    audio_terminal_encode_voice_input_5cec72(&packet);
    uint32_t icon=word(0x1ccu),title=word(0x1d0u);
    uint32_t label=word(0x1d4u),hint=word(0x1dcu);
    if (icon!=0u && title!=0u && label!=0u && hint!=0u) {
        audio_uart_page_43dfa4((void *)(uintptr_t)icon,1u);
        audio_terminal_processing_prepare_5ea30c();
        (void)audio_terminal_set_label_style_5e482a(
            title,audio_terminal_output_style_20003f80,6u,100u);
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)label,thinking);
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)hint,stop_hint);
        audio_terminal_elapsed_refresh_5e4902();
    }
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x4b1u,message);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c000000u,short_message,short_message);
    return 0u;
}
