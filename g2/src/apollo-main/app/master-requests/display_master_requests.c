/* Apollo master display request wrappers 0x464b2e-0x464d1b. */
#include <stdint.h>

extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern int32_t audio_uart_master_request_core_464772(uint32_t,const void *,uint32_t,
                                                      uint32_t,uint32_t,uint32_t,uint32_t);

static const char module[]="sync.module.api";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_interface_api.c";

static void request_log(const char *function,uint32_t line,
                        const char *extended,const char *compact,
                        uint32_t id,uint32_t length,uint32_t exit_request)
{
    uint32_t level=audio_log_level();
    if((level&2u)!=0u) {
        if(exit_request!=0u)
            audio_log_extended(4u,module,source,function,line,extended);
        else
            audio_log_extended(4u,module,source,function,line,extended,id,length);
    }
    level=audio_log_level();
    if((level&1u)!=0u || (audio_log_level()&4u)!=0u) {
        if(exit_request!=0u)
            (void)compressed_log_output(0x10000000u,compact,compact);
        else
            (void)compressed_log_output(0x10800000u,compact,compact,id,length);
    }
}

/* Stock 0x464B2E (RequestDisplayStartUp) */
void audio_uart_master_display_start(uint32_t id,const void *payload,
                                     uint16_t length,uint32_t extra)
{
    id=(uint16_t)id;
    static const char extended[]="REQUEST_DISPLAY_START_UP applictionID = %d,length = %d";
    static const char compact[]="[sync.module.api]REQUEST_DISPLAY_START_UP applictionID = %d,length = %d";
    request_log("RequestDisplayStartUp",0x73u,extended,compact,id,length,0u);
    (void)audio_uart_master_request_core_464772(id,payload,length,extra,1u,2u,0u);
}

/* Stock 0x464BB2 (RequestDisplayReflash) */
void audio_uart_master_display_refresh(uint32_t id,const void *payload,
                                       uint16_t length,uint32_t extra)
{
    id=(uint16_t)id;
    static const char extended[]="REQUEST_DISPLAY_REFLASH applictionID = %d,length = %d";
    static const char compact[]="[sync.module.api]REQUEST_DISPLAY_REFLASH applictionID = %d,length = %d";
    request_log("RequestDisplayReflash",0x79u,extended,compact,id,length,0u);
    (void)audio_uart_master_request_core_464772(id,payload,length,extra,3u,2u,0u);
}

void audio_uart_master_display_stop(uint32_t id,const void *payload,
                                    uint16_t length,uint32_t extra)
{
    id=(uint16_t)id;
    static const char extended[]="REQUEST_DISPLAY_STOP applictionID = %d,length = %d";
    static const char compact[]="[sync.module.api]REQUEST_DISPLAY_STOP applictionID = %d,length = %d";
    request_log("RequestDisplayStop",0x7fu,extended,compact,id,length,0u);
    (void)audio_uart_master_request_core_464772(id,payload,length,extra,5u,2u,0u);
}

/* Stock 0x464CBA (RequestDisplayExit) */
void audio_uart_master_control(uint32_t extra)
{
    static const char extended[]="REQUEST_DISPLAY_EXIT";
    static const char compact[]="[sync.module.api]REQUEST_DISPLAY_EXIT";
    request_log("RequestDisplayExit",0x85u,extended,compact,0u,0u,1u);
    (void)audio_uart_master_request_core_464772(0u,0,0u,extra,0x10u,2u,0u);
}
