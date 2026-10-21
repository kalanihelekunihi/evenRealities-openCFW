/* Terminal FSM ASR failure/timeout action, stock 0x5e5de0..0x5e5ec9. */
#include <stdint.h>
#include "terminal_reset_assets_20261016.h"

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern void audio_terminal_reset_preclear_5e7f26(void);
extern void audio_terminal_asr_timeout_stop_5e7fc0(void);
extern uint32_t audio_terminal_reset_mode_notice_54f50e(uint32_t);
extern void audio_terminal_processing_hide_5e4878(uint32_t);
extern void audio_terminal_ui_stop_service_b_5ec268(void);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void audio_terminal_encode_voice_input_5cec72(const uint8_t *);
extern void audio_uart_page_43dfa4(void *,uint32_t);
extern void audio_terminal_processing_prepare_5ea30c(void);
extern void audio_terminal_image_set_5e47fe(void *,const void *);
extern const char *audio_uart_page_49942e(uint8_t *,const char *);
extern void audio_terminal_elapsed_clear_5e4894(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.ui";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[]="terminal_ui_action_asr_fail";
static const char message[]="asr failed/timeout, back to idle (from state=%d)";
static const char short_message[]="[terminal.ui]asr failed/timeout, back to idle (from state=%d)";
static const char waiting[]="Waiting input";
static const char hint[]="[Tap & hold to input]";
static uint32_t word(uint32_t offset) {
    const uint8_t *p=audio_terminal_ui_state_base+offset;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

uint32_t audio_terminal_ui_action_5e5de0(uint32_t old_state,uint32_t event_payload) {
    (void)event_payload;
    audio_terminal_reset_preclear_5e7f26();
    audio_terminal_asr_timeout_stop_5e7fc0();
    if ((uint8_t)old_state==4u) {
        (void)audio_terminal_reset_mode_notice_54f50e(6u);
        audio_terminal_processing_hide_5e4878(word(0x1f8u));
    }
    audio_terminal_ui_stop_service_b_5ec268();
    uint8_t packet=0u;
    audio_uart_buffer_zero(&packet,1u,0u);
    packet=5u;
    audio_terminal_encode_voice_input_5cec72(&packet);
    uint32_t icon=word(0x1ccu),title=word(0x1d0u);
    uint32_t label=word(0x1d4u),sub=word(0x1dcu);
    if (icon!=0u && title!=0u && label!=0u && sub!=0u) {
        audio_uart_page_43dfa4((void *)(uintptr_t)icon,1u);
        audio_terminal_processing_prepare_5ea30c();
        audio_terminal_image_set_5e47fe((void *)(uintptr_t)title,&audio_terminal_asset_7733a8);
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)label,waiting);
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)sub,hint);
        audio_terminal_elapsed_clear_5e4894();
    }
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(2u,module,path,function,0x4feu,message,(uint8_t)old_state);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x08400000u,short_message,short_message,(uint8_t)old_state);
    return 0u;
}
