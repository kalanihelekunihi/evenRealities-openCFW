/* Native onboarding flag RPC0x47e4a6, with getter0x4a7832 inlined from
 * its authenticated six-byte load at RAM0x20000040. */
#include <stdint.h>
extern volatile uint8_t g2_onboarding_flag; /* cell0x20000040 */
extern uint32_t audio_uart_handshake_send(uint32_t,const void *,uint32_t,
                                          uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                                uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="onboarding.data_mgr";
static const char source_file[]=
 "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\onboarding\\onboarding_data_manager.c";
static const char function_name[]="RPC_OnboardingFlagSendToPeer";
static const char message[]="send flag=%d to peer";
static const char short_message[]="[onboarding.data_mgr]send flag=%d to peer";

void audio_uart_service_prepare5(void) {
    uint8_t flag=g2_onboarding_flag;
    uint8_t packet[2]={0x0du,flag};
    (void)audio_uart_handshake_send(0x10u,packet,2u,0u,5u);
    if(audio_log_flags()&2u)
        audio_log_extended(4u,module,source_file,function_name,0x7fu,
                           message,flag);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x10400000u,short_message,
                                    short_message,flag);
}
