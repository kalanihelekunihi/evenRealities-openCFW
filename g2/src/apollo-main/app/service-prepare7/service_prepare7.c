/* Native ring battery request0x4ff99a, with authenticated send and log ABI. */
#include <stdint.h>
extern uint32_t audio_uart_request_send(uint32_t,const void *,uint32_t,uint32_t); /* 0x4651e0 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                                uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="svc.ring_bat";
static const char source_file[]=
 "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\ring_battery\\service_ring_battery.c";
static const char function_name[]="SVC_RingBattery_RequestFromPeer";
static const char failed[]="SVC_RingBattery_RequestFromPeer send failed: ret=%d";
static const char failed_short[]=
 "[svc.ring_bat]SVC_RingBattery_RequestFromPeer send failed: ret=%d";
static const char sent[]="ring battery request sent to peer";
static const char sent_short[]="[svc.ring_bat]ring battery request sent to peer";

/* Stock 0x4FF99A (SVC_RingBattery_RequestFromPeer) */
void audio_uart_service_prepare7(void) {
    uint8_t request[12]={0};
    request[0]=6u;
    uint32_t result=audio_uart_request_send(0x105u,request,12u,0u);
    if(result!=0u) {
        if(audio_log_flags()&2u)
            audio_log_extended(1u,module,source_file,function_name,0x44u,
                               failed,result);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x04400000u,failed_short,
                                        failed_short,result);
    } else {
        if(audio_log_flags()&2u)
            audio_log_extended(4u,module,source_file,function_name,0x46u,sent);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x10000000u,sent_short,sent_short);
    }
}
