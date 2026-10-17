/* Stock Main BoxDetect_common_data_handler at 0x4acb40. */
#include <stdint.h>

extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
extern uint32_t audio_uart_case_sync_event_510a0c(const uint8_t *,uint32_t);
extern void audio_uart_service_prepare3(uint32_t); /* 0x4ac828 */
extern void audio_uart_case_sync_response_4ac890(const uint8_t *);
extern void audio_uart_case_force_out_4ac5a2(uint8_t);

static const char module[]="box.detect";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\box_detect\\service_box_detect.c";
static const char function_name[]="BoxDetect_common_data_handler";

static void log0(uint8_t level,uint32_t line,const char *message,uint32_t code,const char *compact)
{
    if (audio_log_level()&2u)
        audio_log_extended(level,module,path,function_name,line,message);
    if ((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(code,compact,compact);
}
static void log1(uint8_t level,uint32_t line,const char *message,uint32_t code,
                 const char *compact,uint32_t value)
{
    if (audio_log_level()&2u)
        audio_log_extended(level,module,path,function_name,line,message,value);
    if ((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(code,compact,compact,value);
}
static void log_bad(const uint8_t *raw,uint32_t length)
{
    static const char message[]="Invalid case sync data: raw_data=%p, len=%d";
    static const char compact[]="[box.detect]Invalid case sync data: raw_data=%p, len=%d";
    if (audio_log_level()&2u)
        audio_log_extended(1u,module,path,function_name,0x2fcu,message,raw,length);
    if ((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x04800000u,compact,compact,raw,length);
}

int32_t audio_uart_registry_callback_4acb40(uint32_t event,const uint8_t *raw,
                                               uint32_t length,uint32_t unused)
{
    (void)unused;
    if (event==0u) {
        audio_uart_case_sync_event_510a0c(raw,(uint16_t)length);
        return 0;
    }
    if (event!=5u)
        return -1;
    if (raw==0 || length<8u) {
        log_bad(raw,length);
        return -1;
    }
    switch (raw[0]) {
    case 1u:
        log0(4u,0x305u,"Received case sync request",0x10000000u,
             "[box.detect]Received case sync request");
        audio_uart_service_prepare3(2u);
        return 0;
    case 2u:
        log0(4u,0x30bu,"Received case sync response",0x10000000u,
             "[box.detect]Received case sync response");
        audio_uart_case_sync_response_4ac890(raw);
        return 0;
    case 3u:
        log0(4u,0x311u,"Received case sync notification",0x10000000u,
             "[box.detect]Received case sync notification");
        audio_uart_case_sync_response_4ac890(raw);
        return 0;
    case 4u: {
        uint8_t force=(uint8_t)(raw[7]==0u);
        log1(3u,0x317u,"Received force out box sync: %d",0x0c400000u,
             "[box.detect]Received force out box sync: %d",force);
        audio_uart_case_force_out_4ac5a2(force);
        return 0;
    }
    default:
        log1(2u,0x31cu,"Unknown case sync message ID: %d",0x08400000u,
             "[box.detect]Unknown case sync message ID: %d",raw[0]);
        return -1;
    }
}
