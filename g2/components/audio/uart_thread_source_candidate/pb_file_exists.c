/* Dashboard layout PB-file existence probe, native 0x55876a. The path and
 * "rb" mode are authenticated ROM literals at 0x75f1f0 and 0x5588a4. */
#include <stdint.h>
extern void *audio_file_open(const char *,const char *); /* 0x474550 */
extern int32_t audio_file_close(void *); /* selected 0x4745f4 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char path[]="/configure/dashboard_ext.proto";
static const char mode[]="rb";
static const char module[]="dashboard.layout";
static const char source_file[]=
 "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\dashboard_layout.c";
static const char function_name[]="dashboard_layout_pb_file_exists";
static const char absent[]="layout pb file not found: %s";
static const char absent_short[]="[dashboard.layout]layout pb file not found: %s";
static const char present[]="layout pb file exists: %s";
static const char present_short[]="[dashboard.layout]layout pb file exists: %s";
uint32_t audio_uart_pb_file_exists(void) {
    void *file=audio_file_open(path,mode);
    if(file==0) {
        if(audio_log_flags()&2u)
            audio_log_extended(4u,module,source_file,function_name,0x13fu,
                               absent,path);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x10400000u,absent_short,
                                        absent_short,path);
        return 0u;
    }
    (void)audio_file_close(file);
    if(audio_log_flags()&2u)
        audio_log_extended(4u,module,source_file,function_name,0x143u,
                           present,path);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x10400000u,present_short,
                                    present_short,path);
    return 1u;
}
