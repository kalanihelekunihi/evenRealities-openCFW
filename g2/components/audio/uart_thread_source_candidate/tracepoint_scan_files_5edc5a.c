/* Stock Main tracepoint_scan_files 0x5edc5a. */
#include <stdint.h>

extern uint8_t audio_tracepoint_file_inventory[0x88];
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void *audio_tracepoint_dir_open_474b02(const char *);
extern void *audio_tracepoint_dir_read_474bb8(void *);
extern void audio_tracepoint_dir_close_474c66(void *);
extern int32_t audio_tracepoint_parse_sequence_5edaf0(const char *,uint32_t *);
extern void audio_tracepoint_format_file_path_5edba2(char *,uint32_t,uint32_t);
extern uint32_t audio_tracepoint_file_size_5edb68(const char *);
extern void audio_tracepoint_insert_file_sorted_5edbb0(uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="tp.setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\tracepoint\\tracepoint_setting.c";
static const char function[]="tracepoint_scan_files";
static const char directory[]="/log/tp";
static const char open_fail[]="open tracepoint dir failed: %s";
static const char open_fail_short[]="[tp.setting]open tracepoint dir failed: %s";
static const char file_msg[]="tracepoint scan file: %s seq=%u size=%u";
static const char file_short[]="[tp.setting]tracepoint scan file: %s seq=%u size=%u";
static const char done_msg[]="tracepoint scan done, count=%u total=%u";
static const char done_short[]="[tp.setting]tracepoint scan done, count=%u total=%u";

static uint32_t word_at(uint32_t offset) {
    return *(const uint32_t *)(const void *)(audio_tracepoint_file_inventory+offset);
}
int32_t audio_tracepoint_scan_files_5edc5a(void) {
    audio_uart_buffer_zero(audio_tracepoint_file_inventory,0x88u,0u);
    void *dir=audio_tracepoint_dir_open_474b02(directory);
    if(dir==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,0x85u,open_fail,directory);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04400000u,open_fail_short,open_fail_short,directory);
        return -1;
    }
    void *entry;
    while((entry=audio_tracepoint_dir_read_474bb8(dir))!=0) {
        uint32_t sequence=0;
        if(((const uint8_t *)entry)[0x100u]==8u &&
           audio_tracepoint_parse_sequence_5edaf0((const char *)entry,&sequence)!=0) {
            char full_path[0x50];
            audio_tracepoint_format_file_path_5edba2(full_path,0x50u,sequence);
            uint32_t size=audio_tracepoint_file_size_5edb68(full_path);
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(4u,module,path,function,0x96u,file_msg,entry,sequence,size);
            if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x10c00000u,file_short,file_short,entry,sequence,size);
            audio_tracepoint_insert_file_sorted_5edbb0(sequence,size);
        }
    }
    audio_tracepoint_dir_close_474c66(dir);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,0x9du,done_msg,word_at(0x80u),word_at(0x84u));
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10800000u,done_short,done_short,word_at(0x80u),word_at(0x84u));
    return 0;
}
