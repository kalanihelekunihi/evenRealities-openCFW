/* Stock Main tracepoint_handle_delete_file at 0x5ee488. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint32_t audio_tracepoint_role_char_5edadc(void);
extern int32_t audio_tracepoint_validate_file_name_5ede30(const char *, char *, uint32_t);
extern int32_t audio_tracepoint_resolve_file_path_5eddf6(char *, uint32_t *);
extern void audio_tracepoint_storage_lock_47e088(void);
extern int32_t audio_tracepoint_storage_unlink_47498c(const char *);
extern void audio_tracepoint_make_result_message_5ee10a(uint32_t,uint32_t,uint32_t);
extern void audio_tracepoint_reply_result_5ee134(const uint8_t *);
extern uint8_t audio_tracepoint_reply_buffer[];

static const char module[]="tp.setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\tracepoint\\tracepoint_setting.c";
static const char function[]="tracepoint_handle_delete_file";
static const char null_text[]="null";
static const char request[]="tracepoint delete request magic=%u role=%c file=%s";
static const char request_short[]="[tp.setting]tracepoint delete request magic=%u role=%c file=%s";
static const char mapped[]="tracepoint delete mapped path=%s seq=%u";
static const char mapped_short[]="[tp.setting]tracepoint delete mapped path=%s seq=%u";
static const char deleted[]="tracepoint delete file %s result=%d";
static const char deleted_short[]="[tp.setting]tracepoint delete file %s result=%d";
static const char invalid[]="invalid tracepoint delete file name: %s";
static const char invalid_short[]="[tp.setting]invalid tracepoint delete file name: %s";

void audio_tracepoint_delete_file_5ee488(uint8_t magic,const char *name)
{
    uint32_t failed=1u;
    char resolved[80];
    uint32_t sequence=0;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u,module,path,function,0x162u,request,
                           magic,(uint8_t)audio_tracepoint_role_char_5edadc(),
                           name ? name : null_text);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0cc00000u,request_short,request_short,
                                    magic,(uint8_t)audio_tracepoint_role_char_5edadc(),
                                    name ? name : null_text);
    if (audio_tracepoint_validate_file_name_5ede30(name,resolved,80u)==0) {
        if (audio_tracepoint_resolve_file_path_5eddf6(resolved,&sequence)!=0) {
            if (audio_log_flags() & 2u)
                audio_log_extended(4u,module,path,function,0x169u,mapped,
                                   resolved,sequence);
            if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                (void)compressed_log_output(0x10800000u,mapped_short,mapped_short,
                                            resolved,sequence);
            audio_tracepoint_storage_lock_47e088();
            failed=audio_tracepoint_storage_unlink_47498c(resolved)!=0;
            if (audio_log_flags() & 2u)
                audio_log_extended(3u,module,path,function,0x16cu,deleted,
                                   resolved,failed);
            if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                (void)compressed_log_output(0x0c800000u,deleted_short,deleted_short,
                                            resolved,failed);
        }
    } else {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u,module,path,function,0x16fu,invalid,
                               name ? name : null_text);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x08400000u,invalid_short,invalid_short,
                                        name ? name : null_text);
    }
    audio_tracepoint_make_result_message_5ee10a(2u,magic,failed);
    audio_tracepoint_reply_result_5ee134(audio_tracepoint_reply_buffer);
}
