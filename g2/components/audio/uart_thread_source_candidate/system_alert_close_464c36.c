/* Native RequestDisplayStop 0x464c36. */
#include <stdint.h>
extern int32_t audio_uart_master_request_core_464772(uint32_t,const void *,uint32_t,
                                                      uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="sync.module.api";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_interface_api.c";
static const char function[]="RequestDisplayStop";
static const char message[]="REQUEST_DISPLAY_STOP applictionID = %d,length = %d";
static const char compact[]="[sync.module.api]REQUEST_DISPLAY_STOP applictionID = %d,length = %d";

void audio_system_alert_close_464c36(uint32_t application_id,uint32_t payload,
                                      uint32_t length,uint32_t context) {
    const uint16_t id=(uint16_t)application_id;
    const uint16_t bytes=(uint16_t)length;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,0x7fu,message,id,bytes,context);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10800000u,compact,compact,id,bytes);
    (void)audio_uart_master_request_core_464772(id,(const void *)(uintptr_t)payload,
                                                   bytes,context,5u,2u,0u);
}
