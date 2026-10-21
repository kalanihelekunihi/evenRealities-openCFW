/* Terminal FSM ASR-final action, stock 0x5e5aae..0x5e5bc5. */
#include <stdint.h>
#include "terminal_reset_assets_20261016.h"

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern const uint8_t *audio_td_state_ptr(void);
extern void audio_terminal_reset_preclear_5e7f26(void);
extern void audio_terminal_asr_timeout_stop_5e7fc0(void);
extern uint32_t audio_terminal_reset_mode_notice_54f50e(uint32_t);
extern void audio_terminal_processing_hide_5e4878(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_terminal_ui_notification_restore_5ebfae(uint32_t);
extern void audio_terminal_ui_result_area_prepare_5ebff8(void);
extern void audio_uart_page_43dfa4(void *,uint32_t);
extern void audio_terminal_processing_prepare_5ea30c(void);
extern void audio_terminal_image_set_5e47fe(void *,const void *);
extern const char *audio_uart_page_49942e(uint8_t *,const char *);
extern void audio_terminal_elapsed_clear_5e4894(void);

static const char module[]="terminal.ui";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[]="terminal_ui_action_asr_final";
static const char forced[]="ASR final received while capturing, force release audio";
static const char forced_short[]="[terminal.ui]ASR final received while capturing, force release audio";
static const char shown[]="ASR final received, showing confirm/cancel";
static const char shown_short[]="[terminal.ui]ASR final received, showing confirm/cancel";
static const char prompt[]="Confirm input?";
static const char hint[]="[Swipe to select]";
static uint32_t word(uint32_t offset) {
    const uint8_t *p=audio_terminal_ui_state_base+offset;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

uint32_t audio_terminal_ui_action_5e5aae(uint32_t old_state,uint32_t event_payload) {
    (void)event_payload;
    audio_terminal_reset_preclear_5e7f26();
    audio_terminal_asr_timeout_stop_5e7fc0();
    if ((uint8_t)old_state==4u) {
        (void)audio_terminal_reset_mode_notice_54f50e(6u);
        audio_terminal_processing_hide_5e4878(word(0x1f8u));
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x481u,forced);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08000000u,forced_short,forced_short);
    }
    const uint8_t *state=audio_td_state_ptr();
    if (*(const uint16_t *)(const void *)(state+0x802u)!=0u)
        audio_terminal_ui_notification_restore_5ebfae((uint32_t)(uintptr_t)state);
    audio_terminal_ui_result_area_prepare_5ebff8();
    uint32_t icon=word(0x1ccu),title=word(0x1d0u);
    uint32_t label=word(0x1d4u),sub=word(0x1dcu);
    if (icon!=0u && title!=0u && label!=0u && sub!=0u) {
        audio_uart_page_43dfa4((void *)(uintptr_t)icon,1u);
        audio_terminal_processing_prepare_5ea30c();
        audio_terminal_image_set_5e47fe((void *)(uintptr_t)title,&audio_terminal_asset_7733a8);
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)label,prompt);
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)sub,hint);
        audio_terminal_elapsed_clear_5e4894();
    }
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x492u,shown);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c000000u,shown_short,shown_short);
    return 0u;
}
