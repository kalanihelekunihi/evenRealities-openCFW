/* Terminal FSM voice-stop action, stock 0x5e598a..0x5e5a7d. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern const uint8_t *audio_td_state_ptr(void);
extern const uint8_t audio_terminal_voice_icon_773044;
extern void audio_terminal_reset_preclear_5e7f26(void);
extern void audio_terminal_asr_timeout_start_5e7f6e(void);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void audio_terminal_encode_voice_input_5cec72(const uint8_t *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint32_t audio_terminal_reset_mode_notice_54f50e(uint32_t);
extern void audio_terminal_processing_hide_5e4878(uint32_t);
extern void audio_uart_page_43dfa4(void *,uint32_t);
extern void audio_terminal_processing_prepare_5ea30c(void);
extern void audio_terminal_image_set_5e47fe(void *,const void *);
extern const char *audio_uart_page_49942e(uint8_t *,const char *);
extern void audio_terminal_elapsed_clear_5e4894(void);
extern void audio_terminal_ui_notification_restore_5ebfae(uint32_t);
extern void audio_terminal_ui_processing_label_5ebfe0(void);

static const char module[]="terminal.ui";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[]="terminal_ui_action_voice_stop";
static const char message[]="voice stop manual";
static const char short_message[]="[terminal.ui]voice stop manual";
static const char recognizing[]="Recognizing...";
static const char waiting[]="Waiting for result...";
static const char empty[]="";

static uint32_t word(uint32_t offset) {
    const uint8_t *p=audio_terminal_ui_state_base+offset;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

uint32_t audio_terminal_ui_action_5e598a(uint32_t old_state,uint32_t event_payload) {
    (void)old_state;
    audio_terminal_reset_preclear_5e7f26();
    audio_terminal_asr_timeout_start_5e7f6e();
    if (event_payload==0u) {
        uint8_t packet=0u;
        audio_uart_buffer_zero(&packet,1u,0u);
        packet=2u;
        audio_terminal_encode_voice_input_5cec72(&packet);
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,0x443u,message);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c000000u,short_message,short_message);
    }
    (void)audio_terminal_reset_mode_notice_54f50e(6u);
    audio_terminal_processing_hide_5e4878(word(0x1f8u));
    uint32_t icon=word(0x1ccu),title=word(0x1d0u);
    uint32_t hint=word(0x1d4u),elapsed=word(0x1dcu);
    if (icon!=0u && title!=0u && hint!=0u && elapsed!=0u) {
        audio_uart_page_43dfa4((void *)(uintptr_t)icon,1u);
        audio_terminal_processing_prepare_5ea30c();
        audio_terminal_image_set_5e47fe((void *)(uintptr_t)title,&audio_terminal_voice_icon_773044);
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)hint,recognizing);
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)elapsed,empty);
        audio_terminal_elapsed_clear_5e4894();
    }
    const uint8_t *state=audio_td_state_ptr();
    if (*(const uint16_t *)(const void *)(state+0x802u)!=0u)
        audio_terminal_ui_notification_restore_5ebfae((uint32_t)(uintptr_t)state);
    else
        audio_terminal_ui_notification_restore_5ebfae((uint32_t)(uintptr_t)waiting);
    audio_terminal_ui_processing_label_5ebfe0();
    return 0u;
}
