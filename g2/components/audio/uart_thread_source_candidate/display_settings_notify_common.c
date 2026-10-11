/* Native setting_notify_common 0x49bbfc, with nanopb stream handoff. */
#include <stdint.h>
struct pb_ostream_candidate {void *callback;void *state;uint32_t max_size;uint32_t bytes_written;const char *errmsg;};
_Static_assert(sizeof(struct pb_ostream_candidate)==20u,"nanopb ostream ABI");
extern uint8_t audio_settings_notify_staging[104]; /* RAM 0x200725a0 */
extern uint8_t audio_settings_notify_encode_buffer[256]; /* RAM 0x200706ec */
extern uint32_t audio_settings_notify_magic; /* RAM 0x2007486c */
extern const uint8_t audio_settings_status_pb_descriptor[]; /* ROM 0x77772c */
extern uint8_t audio_uart_device_role_get(void); /* selected 0x45a568 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern void audio_uart_checksum_copy(void *,const void *,uint32_t); /* selected 0x439c04 */
extern void audio_pb_ostream_from_buffer(struct pb_ostream_candidate *,void *,uint32_t); /* native 0x4905f4 */
extern uint32_t audio_pb_encode(struct pb_ostream_candidate *,const void *,const void *); /* native 0x490c32 */
extern uint32_t audio_settings_notify_ble(uint32_t,uint32_t,const void *,uint32_t); /* native 0x475c1a */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="pb_service_setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_setting\\pb_service_setting.c";
static const char function[]="setting_notify_common";
static const char null_message[]="pPackage is NULL";
static const char null_short[]="[pb_service_setting]pPackage is NULL";
static const char not_master[]="not master role, not send";
static const char not_master_short[]="[pb_service_setting]not master role, not send";
static const char notify_message[]="[Notify] command_id = %d, magic_random = %d";
static const char notify_short[]="[pb_service_setting][Notify] command_id = %d, magic_random = %d";
static const char encode_message[]="Encoding failed: %s";
static const char encode_short[]="[pb_service_setting]Encoding failed: %s";
static const char encoded_message[]="[Notify] BLE sent successfully, size = %d";
static const char encoded_short[]="[pb_service_setting][Notify] BLE sent successfully, size = %d";
static const char none[]="(none)";
static void store32(uint8_t *p,uint32_t v) {p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);}
uint32_t audio_settings_notify_common(uint8_t *packet) {
    if(audio_uart_device_role_get()!=1u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(4u,module,path,function,359u,not_master);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x10000000u,not_master_short,not_master_short);
        return 0u;
    }
    if(packet==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,366u,null_message);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,null_short,null_short);
        return 1u;
    }
    audio_uart_buffer_zero(audio_settings_notify_staging,104u,0u);
    audio_uart_checksum_copy(audio_settings_notify_staging,packet,104u);
    audio_settings_notify_magic++;
    store32(audio_settings_notify_staging+4u,audio_settings_notify_magic);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,376u,notify_message,
                           audio_settings_notify_staging[0],audio_settings_notify_magic);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10800000u,notify_short,notify_short,
                                    audio_settings_notify_staging[0],audio_settings_notify_magic);
    struct pb_ostream_candidate stream;
    audio_pb_ostream_from_buffer(&stream,audio_settings_notify_encode_buffer,256u);
    if(audio_pb_encode(&stream,audio_settings_status_pb_descriptor,audio_settings_notify_staging)==0u) {
        const char *why=stream.errmsg!=0?stream.errmsg:none;
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,381u,encode_message,why);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04400000u,encode_short,encode_short,why);
        return 43u;
    }
    if(audio_uart_device_role_get()==1u)
        (void)audio_settings_notify_ble(1u,9u,audio_settings_notify_encode_buffer,
                                        (uint16_t)stream.bytes_written);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,389u,encoded_message,stream.bytes_written);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10400000u,encoded_short,encoded_short,stream.bytes_written);
    return 0u;
}
