/* Apollo terminal_action_heart_beat, native 0x5e9ab8. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_action_heart_beat";
static const char message[]="recv terminal heart beat";
static const char short_message[]="[terminal.pb]recv terminal heart beat";

uint32_t audio_terminal_command_5e9ab8(const void *payload,uint32_t length) {
    (void)payload;
    (void)length;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,649u,message);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c000000u,short_message,short_message);
    return 0;
}
