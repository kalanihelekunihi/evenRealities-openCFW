/* Native setting_respond_with_local_data 0x49b7c4..0x49b900. */
#include <stdint.h>
struct pb_ostream_local_candidate {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
};
_Static_assert(sizeof(struct pb_ostream_local_candidate)==20u,"nanopb ostream ABI");
struct pb_msgdesc_candidate;
extern uint8_t audio_settings_notify_staging[104];
extern uint32_t audio_settings_response_magic_20074864;
extern const struct pb_msgdesc_candidate audio_settings_status_pb_descriptor;
extern uint32_t audio_settings_build_full_status(uint8_t *);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern void audio_pb_ostream_from_buffer(struct pb_ostream_local_candidate *,void *,uint32_t);
extern uint32_t audio_pb_encode(struct pb_ostream_local_candidate *,const void *,const void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="pb_service_setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_setting\\pb_service_setting.c";
static const char function[]="setting_respond_with_local_data";
static const char build_failed[]="Failed to build status package";
static const char build_failed_short[]="[pb_service_setting]Failed to build status package";
static const char encode_failed[]="pb_encode failed";
static const char encode_failed_short[]="[pb_service_setting]pb_encode failed";
static const char sent[]="[Respond Local Data] Sent %d bytes, magic=%d";
static const char sent_short[]="[pb_service_setting][Respond Local Data] Sent %d bytes, magic=%d";
static void store32(uint8_t *p,uint32_t v) {
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);
}
uint32_t audio_setting_local_response_encode_49b7c4(uint8_t *output,uint32_t *length) {
    if(output==0 || length==0 || *length==0u)return 0u;
    if(audio_settings_build_full_status(audio_settings_notify_staging)==0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,0x103u,build_failed);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,build_failed_short,build_failed_short);
        return 0u;
    }
    store32(audio_settings_notify_staging+4u,audio_settings_response_magic_20074864);
    struct pb_ostream_local_candidate initial;
    audio_pb_ostream_from_buffer(&initial,output,*length);
    struct pb_ostream_local_candidate stream;
    audio_uart_checksum_copy(&stream,&initial,20u);
    if(audio_pb_encode(&stream,&audio_settings_status_pb_descriptor,
                       audio_settings_notify_staging)==0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,0x10du,encode_failed);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,encode_failed_short,encode_failed_short);
        return 0u;
    }
    *length=stream.bytes_written;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,0x112u,sent,
                           *length,audio_settings_response_magic_20074864);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10800000u,sent_short,sent_short,
                                    *length,audio_settings_response_magic_20074864);
    return 1u;
}
