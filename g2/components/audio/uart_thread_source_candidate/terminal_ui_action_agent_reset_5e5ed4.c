/* Terminal FSM agent-reset action, stock 0x5e5ed4..0x5e5fef. */
#include <stdint.h>
#include "terminal_reset_assets_20261016.h"

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern void audio_terminal_reset_preclear_5e7f26(void);
extern void audio_terminal_asr_timeout_stop_5e7fc0(void);
extern void audio_terminal_ui_stop_service_b_5ec268(void);
extern void audio_terminal_ui_stop_service_c_5ebbc6(void);
extern void audio_terminal_ui_stop_service_d_5ec770(void);
extern void audio_terminal_ui_stop_service_e_5ec9c0(void);
extern void audio_terminal_reset_ancillary_5e65f8(void);
extern void audio_terminal_reset_mode_5eae2c(uint32_t);
extern void audio_terminal_reset_display_5e4c84(uint32_t);
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
static const char function[]="terminal_ui_action_agent_reset";
static const char blocked[]="agent reset while blocked, keep blocked UI";
static const char blocked_short[]="[terminal.ui]agent reset while blocked, keep blocked UI";
static const char cleared[]="agent reset, runtime cleared, back to idle";
static const char cleared_short[]="[terminal.ui]agent reset, runtime cleared, back to idle";
static const char waiting[]="Waiting input";
static const char hint[]="[Tap & hold to input]";
static uint32_t word(uint32_t offset) {
    const uint8_t *p=audio_terminal_ui_state_base+offset;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void zero_word(uint32_t offset) {
    uint8_t *p=audio_terminal_ui_state_base+offset;
    p[0]=0u;p[1]=0u;p[2]=0u;p[3]=0u;
}

uint32_t audio_terminal_ui_action_5e5ed4(uint32_t old_state,uint32_t event_payload) {
    (void)event_payload;
    audio_terminal_reset_preclear_5e7f26();
    audio_terminal_asr_timeout_stop_5e7fc0();
    audio_terminal_ui_stop_service_b_5ec268();
    audio_terminal_ui_stop_service_c_5ebbc6();
    audio_terminal_ui_stop_service_d_5ec770();
    audio_terminal_ui_stop_service_e_5ec9c0();
    audio_terminal_reset_ancillary_5e65f8();
    audio_terminal_ui_state_base[0x280u]=0u;
    zero_word(0x284u);
    audio_terminal_reset_mode_5eae2c(4u);
    if ((uint8_t)old_state==3u) {
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,0x519u,blocked);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c000000u,blocked_short,blocked_short);
        return 4u;
    }
    audio_terminal_reset_display_5e4c84(0u);
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
        audio_log_extended(3u,module,path,function,0x526u,cleared);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c000000u,cleared_short,cleared_short);
    return 0u;
}
