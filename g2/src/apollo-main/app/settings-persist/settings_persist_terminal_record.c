/* Native SVC_KvdbWriteTerminalMode 0x4b04c4. */
#include <stdint.h>

uint8_t audio_settings_terminal_record[4]; /* native RAM 0x20003808 */
extern uint16_t audio_uart_hand_checksum_49acd4(const void *,uint32_t,const uint16_t *);
extern int32_t audio_settings_kvdb_blob_write(const char *,const void *,uint32_t); /* 0x4d957e */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char key[]="kvTerminalMode";
static const char module[]="kv.terminal_mode";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\kv\\service_kvdb_terminal_mode.c";
static const char function[]="SVC_KvdbWriteTerminalMode";
static const char message[]="write terminal mode failed, ret = %d";
static const char short_message[]="[kv.terminal_mode]write terminal mode failed, ret = %d";

/* Stock 0x4B04C4 (SVC_KvdbWriteTerminalMode) */
uint32_t audio_settings_persist_record(const void *source) {
    const uint8_t *bytes=(const uint8_t *)source;
    for(uint32_t i=0u;i<4u;i++) audio_settings_terminal_record[i]=bytes[i];
    audio_settings_terminal_record[0]=1u;
    uint16_t checksum=audio_uart_hand_checksum_49acd4(audio_settings_terminal_record,2u,0);
    audio_settings_terminal_record[2]=(uint8_t)checksum;
    audio_settings_terminal_record[3]=(uint8_t)(checksum>>8);
    int32_t status=audio_settings_kvdb_blob_write(key,audio_settings_terminal_record,4u);
    if(status!=0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,48u,message,status);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04400000u,short_message,short_message,status);
    }
    return 0u;
}
