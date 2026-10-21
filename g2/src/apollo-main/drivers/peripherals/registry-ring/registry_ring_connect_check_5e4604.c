/* Apollo terminal_data_recv_handler 0x5e4604. */
#include <stdint.h>

extern uint32_t audio_terminal_command_route_5ea028(uint32_t,const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal.c";
static const char function[]="terminal_data_recv_handler";
static const char ignore_message[]="ignore terminal query reply from app";
static const char ignore_short[]="[terminal]ignore terminal query reply from app";
static const char unknown_message[]="unsupported terminal command id=%d";
static const char unknown_short[]="[terminal]unsupported terminal command id=%d";

uint32_t audio_registry_ring_connect_check_5e4604(const uint8_t *command) {
    if(command==0) return UINT32_MAX;
    uint32_t id=command[0],route=0u,length=0u;
    switch(id) {
    case 1u: route=1u;length=2u;break;
    case 2u: route=2u;length=2u;break;
    case 3u: route=3u;length=516u;break;
    case 4u: route=4u;length=8u;break;
    case 5u: route=5u;length=532u;break;
    case 6u: route=6u;length=2124u;break;
    case 7u: route=8u;length=1u;break;
    case 8u: route=9u;length=1372u;break;
    case 9u: route=10u;length=1u;break;
    case 10u: route=12u;length=4u;break;
    case 11u: route=11u;length=1u;break;
    case 255u: route=7u;length=1u;break;
    case 163u:
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,227u,ignore_message);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c000000u,ignore_short,ignore_short);
        return 0u;
    default:
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,245u,unknown_message,id);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08400000u,unknown_short,unknown_short,id);
        return UINT32_MAX;
    }
    return audio_terminal_command_route_5ea028(route,command+4u,length);
}
