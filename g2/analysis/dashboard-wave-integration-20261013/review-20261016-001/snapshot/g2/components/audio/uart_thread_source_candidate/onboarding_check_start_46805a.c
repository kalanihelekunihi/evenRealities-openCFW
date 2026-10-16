/* Native onboarding flag getter 0x4a7832 and startup check 0x46805a. */
#include <stdint.h>
extern volatile uint8_t g2_onboarding_flag;
extern uint32_t audio_log_wake_allowed(void);
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t);
extern void audio_uart_master_display_start(uint32_t,const void *,uint16_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="onboarding";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\onboarding\\onboarding.c";
static const char function[]="onboarding_check_start_disp";
static const char message[]="need to request onboarding start up";
static const char short_message[]="[onboarding]need to request onboarding start up";
__attribute__((noinline)) uint32_t audio_onboarding_flag_get_4a7832(void) {return g2_onboarding_flag;}
void audio_wear_child_46805a(uint32_t unused) {
    (void)unused;
    if((uint8_t)audio_onboarding_flag_get_4a7832()!=1u)return;
    if(audio_log_wake_allowed()!=0u &&
       audio_quicklist_refresh_enabled_4434d0(0x10u)==1u)return;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x83u,message);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c000000u,short_message,short_message);
    audio_uart_master_display_start(0x10u,0,0u,0u);
}
