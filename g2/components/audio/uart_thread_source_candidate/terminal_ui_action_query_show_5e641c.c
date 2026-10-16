/* Terminal FSM query-show action, stock 0x5e641c..0x5e652f. */
#include <stdint.h>
#include "terminal_reset_assets_20261016.h"

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern void audio_terminal_reset_display_5e4c84(uint32_t);
extern void audio_terminal_ui_stop_service_e_5ec9c0(void);
extern void audio_terminal_reset_ancillary_5e65f8(void);
extern void audio_uart_page_43dfa4(void *,uint32_t);
extern void audio_terminal_reset_mode_5eae2c(uint32_t);
extern void audio_terminal_query_construct_5eb8da(void);
extern uint32_t audio_terminal_query_hit_test_5eb61e(uint32_t);
extern void audio_terminal_query_layout_5ebb96(void);
extern void audio_terminal_processing_prepare_5ea30c(void);
extern void audio_terminal_image_set_5e47fe(void *,const void *);
extern const char *audio_uart_page_49942e(uint8_t *,const char *);
extern void audio_terminal_elapsed_clear_5e4894(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.ui";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[]="terminal_ui_action_query_show";
static const char message[]="query panel shown: from_state=%d refresh=%lu";
static const char short_message[]="[terminal.ui]query panel shown: from_state=%d refresh=%lu";
static const char title[]="Select an option";
static const char hint[]="[Swipe & tap]";
static uint32_t word(uint32_t offset) {
    const uint8_t *p=audio_terminal_ui_state_base+offset;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

uint32_t audio_terminal_ui_action_5e641c(uint32_t old_state,uint32_t refresh) {
    audio_terminal_reset_display_5e4c84(0u);
    audio_terminal_ui_stop_service_e_5ec9c0();
    audio_terminal_reset_ancillary_5e65f8();
    if (word(0u)!=0u)
        audio_uart_page_43dfa4((void *)(uintptr_t)word(0u),1u);
    if ((uint8_t)refresh!=0u)
        audio_terminal_reset_mode_5eae2c((uint8_t)refresh);
    audio_terminal_query_construct_5eb8da();
    if (word(0x214u)!=0u) {
        audio_terminal_ui_state_base[0x27cu]=
            audio_terminal_query_hit_test_5eb61e(2u)==0u ? 1u : 0u;
        audio_terminal_ui_state_base[0x279u]=0u;
        audio_terminal_query_layout_5ebb96();
    }
    uint32_t icon=word(0x1ccu),image=word(0x1d0u);
    uint32_t label=word(0x1d4u),sub=word(0x1dcu);
    if (icon!=0u && image!=0u && label!=0u && sub!=0u) {
        audio_uart_page_43dfa4((void *)(uintptr_t)icon,1u);
        audio_terminal_processing_prepare_5ea30c();
        audio_terminal_image_set_5e47fe((void *)(uintptr_t)image,&audio_terminal_asset_7733a8);
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)label,title);
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)sub,hint);
        audio_terminal_elapsed_clear_5e4894();
    }
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x5c1u,message,
                           (uint32_t)(uint8_t)old_state,refresh);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c800000u,short_message,short_message,
                                    (uint32_t)(uint8_t)old_state,refresh);
    return 0u;
}
