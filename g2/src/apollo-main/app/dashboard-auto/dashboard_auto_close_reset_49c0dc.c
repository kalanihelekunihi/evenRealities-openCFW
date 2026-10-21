/* Native dashboard auto-close reset 0x49c0dc..0x49c146, RAM 0x200743d0/d4. */
#include <stdint.h>
extern uint32_t audio_log_wake_allowed(void); /* 0x443484 */
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
/* Bounded neighboring cells; final linker placement and complete allocation extent remain open. */
__attribute__((section(".noinit.dashboard_auto_close_200743d0"),aligned(4)))
volatile uint32_t audio_dashboard_auto_close_current_200743d0;
__attribute__((section(".noinit.dashboard_auto_close_200743d4"),aligned(4)))
volatile uint32_t audio_dashboard_auto_close_default_200743d4;
static const char module[]="dashboard";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\dashboard.c";
static const char function[]="dashboard_reset_auto_close_timeout";
static const char message[]="dashboard reset auto close timeout to %d";
static const char compact[]="[dashboard]dashboard reset auto close timeout to %d";
void audio_dashboard_auto_close_reset_49c0dc(void) {
    if(audio_log_wake_allowed()!=1u || audio_quicklist_refresh_enabled_4434d0(1u)!=1u)
        return;
    audio_dashboard_auto_close_current_200743d0=audio_dashboard_auto_close_default_200743d4;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,0x7eu,message,
                           audio_dashboard_auto_close_default_200743d4);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10400000u,compact,compact,
                                    audio_dashboard_auto_close_default_200743d4);
}
