/* Native setting_parse_data_package 0x49b1f8..0x49b3d4. */
#include <stdint.h>
struct pb_istream_setting {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *errmsg;
};
_Static_assert(sizeof(struct pb_istream_setting)==16u,"nanopb stream ABI");
struct pb_msgdesc_candidate;
extern const struct pb_msgdesc_candidate audio_settings_status_pb_descriptor;
extern uint32_t audio_settings_response_command_id_20074860;
extern uint32_t audio_settings_response_magic_20074864;
extern void audio_uart_pb_stream_init(struct pb_istream_setting *,const void *,uint32_t);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern uint32_t audio_uart_pb_decode(void *,const void *,void *);
extern uint32_t audio_setting_is_duplicate_message_49b198(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="pb_service_setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_setting\\pb_service_setting.c";
static const char function[]="setting_parse_data_package";
static const char none[]="(none)";
static const char null_message[]="data or message is NULL";
static const char null_short[]="[pb_service_setting]data or message is NULL";
static const char failed[]="decode failed: %s";
static const char failed_short[]="[pb_service_setting]decode failed: %s";
static const char decoded[]="decode successful: command_id = %d, which_command_data = %d";
static const char decoded_short[]="[pb_service_setting]decode successful: command_id = %d, which_command_data = %d";
static const char duplicate[]="Ignore duplicate message, magic_random = %d";
static const char duplicate_short[]="[pb_service_setting]Ignore duplicate message, magic_random = %d";
static const char success[]="setting data package parsed successfully";
static const char success_short[]="[pb_service_setting]setting data package parsed successfully";
static uint32_t load32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
uint32_t audio_setting_parse_data_package_49b1f8(const uint8_t *data,uint32_t length,uint8_t *message) {
    if(data==0 || message==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,0x65u,null_message);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,null_short,null_short);
        return 0u;
    }
    struct pb_istream_setting initial,stream;
    audio_uart_pb_stream_init(&initial,data,length);
    audio_uart_checksum_copy(&stream,&initial,16u);
    if((uint8_t)audio_uart_pb_decode(&stream,&audio_settings_status_pb_descriptor,message)==0u) {
        const char *error=stream.errmsg?stream.errmsg:none;
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,0x6du,failed,error);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04400000u,failed_short,failed_short,error);
        return 0u;
    }
    uint32_t command=message[0];
    uint32_t which=(uint32_t)message[8]|((uint32_t)message[9]<<8);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,0x72u,decoded,command,which);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10800000u,decoded_short,decoded_short,command,which);
    uint32_t magic=load32(message+4u);
    if(audio_setting_is_duplicate_message_49b198(magic)!=0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x76u,duplicate,magic);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08400000u,duplicate_short,duplicate_short,magic);
        return 0u;
    }
    audio_settings_response_command_id_20074860=command;
    audio_settings_response_magic_20074864=magic;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,0x7eu,success);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10000000u,success_short,success_short);
    return 1u;
}
