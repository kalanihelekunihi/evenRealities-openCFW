/* Apollo terminal_request_display 0x5e43d2 with 0x464bb2 refresh contract. */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void);
extern uint32_t audio_terminal_display_queue_handle; /* native RAM 0x20074a90 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern int32_t audio_uart_master_request_core_464772(uint32_t,const void *,uint32_t,
                                                      uint32_t,uint32_t,uint32_t,uint32_t);

static const char terminal_module[]="terminal";
static const char terminal_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal.c";
static const char terminal_function[]="terminal_request_display";
static const char missing_message[]="terminal is not initialized, ignore display request";
static const char missing_short[]="[terminal]terminal is not initialized, ignore display request";
static const char sync_module[]="sync.module.api";
static const char sync_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_interface_api.c";
static const char sync_function[]="RequestDisplayReflash";
static const char refresh_message[]="REQUEST_DISPLAY_REFLASH applictionID = %d,length = %d";
static const char refresh_short[]="[sync.module.api]REQUEST_DISPLAY_REFLASH applictionID = %d,length = %d";

struct display_request {
    uint8_t event;
    uint8_t reserved[3];
    uint32_t value;
};
_Static_assert(sizeof(struct display_request)==8u,"display request size");

uint32_t audio_terminal_request_display(uint8_t event,uint32_t value) {
    if(audio_uart_device_role_get()!=1u) return 0u;
    struct display_request request={event,{0,0,0},value};
    if(audio_terminal_display_queue_handle==0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,terminal_module,terminal_path,terminal_function,
                               97u,missing_message);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08000000u,missing_short,missing_short);
        return 0u;
    }
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,sync_module,sync_path,sync_function,121u,
                           refresh_message,48u,8u);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10800000u,refresh_short,refresh_short,
                                    48u,8u);
    return (uint32_t)audio_uart_master_request_core_464772(48u,&request,8u,
                                                             0u,3u,2u,0u);
}
