/* Apollo terminal_machine_handler 0x5ea028. */
#include <stdint.h>

typedef uint32_t (*audio_terminal_command_handler)(const void *,uint32_t);
extern const audio_terminal_command_handler audio_terminal_command_handlers[13];
extern const char *audio_terminal_event_name_5ea004(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_machine_handler";
static const char invalid_message[]="invalid terminal event=%d";
static const char invalid_short[]="[terminal.pb]invalid terminal event=%d";
static const char received_message[]="recv terminal event=%d(%s)";
static const char received_short[]="[terminal.pb]recv terminal event=%d(%s)";
static const char unsupported_message[]="unsupported terminal event=%d(%s)";
static const char unsupported_short[]="[terminal.pb]unsupported terminal event=%d(%s)";

uint32_t audio_terminal_command_route_5ea028(uint32_t event,
                                               const void *payload,
                                               uint32_t length) {
    uint32_t id=(uint8_t)event;
    if(id>=13u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,835u,invalid_message,id);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08400000u,invalid_short,invalid_short,id);
        return UINT32_MAX;
    }
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,839u,received_message,
                           id,audio_terminal_event_name_5ea004(id));
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c800000u,received_short,received_short,
                                    id,audio_terminal_event_name_5ea004(id));
    audio_terminal_command_handler handler=audio_terminal_command_handlers[id];
    if(handler==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,843u,unsupported_message,
                               id,audio_terminal_event_name_5ea004(id));
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08800000u,unsupported_short,
                                        unsupported_short,id,
                                        audio_terminal_event_name_5ea004(id));
        return UINT32_MAX;
    }
    return handler(payload,length);
}
