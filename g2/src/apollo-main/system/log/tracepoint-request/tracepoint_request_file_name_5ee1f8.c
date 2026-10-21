/* Stock Main tracepoint_handle_request_file_name 0x5ee1f8. */
#include <stdint.h>

extern uint8_t audio_tracepoint_reply_buffer[0x206];
extern uint8_t audio_tracepoint_file_inventory[0x88];
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern uint32_t audio_tracepoint_role_char_5edadc(void);
extern void audio_tracepoint_reset_pull_478110(uint8_t);
extern int32_t audio_tracepoint_prepare_pull_48ec9e(void);
extern int32_t audio_tracepoint_scan_files_5edc5a(void);
extern int32_t audio_tracepoint_format_list_name_5eddc8(uint32_t,uint32_t,char *,uint32_t);
extern uint8_t audio_uart_device_role_get(void);
extern uint32_t audio_tracepoint_send_to_master_5ee066(uint32_t,const uint8_t *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

uint8_t audio_tracepoint_local_file_list_ready
    __attribute__((section(".bss.opencfw.tracepoint.file_list_ready"),used));

static const char module[]="tp.setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\tracepoint\\tracepoint_setting.c";
static const char function[]="tracepoint_handle_request_file_name";
static const char req[]="tracepoint request file list magic=%u role=%c";
static const char req_short[]="[tp.setting]tracepoint request file list magic=%u role=%c";
static const char prep_fail[]="tracepoint prepare pull failed: %d";
static const char prep_fail_short[]="[tp.setting]tracepoint prepare pull failed: %d";
static const char scan_fail[]="tracepoint scan failed, return empty file list";
static const char scan_fail_short[]="[tp.setting]tracepoint scan failed, return empty file list";
static const char entry_msg[]="tracepoint file list[%u]=%s seq=%u size=%u";
static const char entry_short[]="[tp.setting]tracepoint file list[%u]=%s seq=%u size=%u";
static const char slave_fail[]="tracepoint slave send file list failed ret=%d";
static const char slave_fail_short[]="[tp.setting]tracepoint slave send file list failed ret=%d";
static const char master_msg[]="tracepoint master local file list stored count=%u";
static const char master_short[]="[tp.setting]tracepoint master local file list stored count=%u";

static uint32_t word_at(const uint8_t *p,uint32_t offset) {
    return *(const uint32_t *)(const void *)(p+offset);
}
static void half_at(uint8_t *p,uint32_t offset,uint16_t value) {
    *(uint16_t *)(void *)(p+offset)=value;
}
void audio_tracepoint_request_file_name_5ee1f8(uint8_t magic) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x126u,req,magic,audio_tracepoint_role_char_5edadc());
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c800000u,req_short,req_short,magic,audio_tracepoint_role_char_5edadc());
    audio_tracepoint_reset_pull_478110(0u);
    int32_t prepared=audio_tracepoint_prepare_pull_48ec9e();
    if(prepared!=0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x12cu,prep_fail,prepared);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08400000u,prep_fail_short,prep_fail_short,prepared);
    }
    if(audio_tracepoint_scan_files_5edc5a()!=0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x131u,scan_fail);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08000000u,scan_fail_short,scan_fail_short);
    }
    audio_uart_buffer_zero(audio_tracepoint_reply_buffer,0x206u,0u);
    audio_tracepoint_reply_buffer[0]=1u;
    audio_tracepoint_reply_buffer[1]=magic;
    half_at(audio_tracepoint_reply_buffer,2u,3u);
    uint32_t role=audio_tracepoint_role_char_5edadc();
    uint32_t count=word_at(audio_tracepoint_file_inventory,0x80u);
    if(count>16u) count=16u;
    half_at(audio_tracepoint_reply_buffer,4u,(uint16_t)count);
    for(uint32_t i=0;i<count;i++) {
        char *name=(char *)(void *)(audio_tracepoint_reply_buffer+6u+i*0x20u);
        uint32_t sequence=word_at(audio_tracepoint_file_inventory,i*8u);
        uint32_t size=word_at(audio_tracepoint_file_inventory,i*8u+4u);
        (void)audio_tracepoint_format_list_name_5eddc8(sequence,role,name,0x20u);
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(4u,module,path,function,0x14bu,entry_msg,i,name,sequence,size);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x11000000u,entry_short,entry_short,i,name,sequence,size);
    }
    if(audio_uart_device_role_get()==2u) {
        int32_t result=(int32_t)audio_tracepoint_send_to_master_5ee066(0xbu,audio_tracepoint_reply_buffer);
        if(result!=0) {
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(1u,module,path,function,0x152u,slave_fail,result);
            if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x04400000u,slave_fail_short,slave_fail_short,result);
        }
    } else {
        audio_tracepoint_local_file_list_ready=1u;
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(4u,module,path,function,0x157u,master_msg,count);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x10400000u,master_short,master_short,count);
    }
}
