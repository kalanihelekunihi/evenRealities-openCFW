/* Stock Main BoxDetect_SetForceOutBox 0x4ac5a2. */
#include <stdint.h>
extern volatile uint8_t audio_uart_case_status_disabled; /* same stock cell 0x20075012 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
extern void audio_uart_case_force_out_apply_4ac798(void);
extern void audio_uart_case_display_refresh_4abf86(void);
extern void audio_uart_case_notify_4abec8(void);
extern void audio_uart_display_housekeep(void); /* 0x47243a */
extern void audio_uart_case_force_out_finish_4ac19c(uint32_t);

static const char module[]="box.detect";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\box_detect\\service_box_detect.c";
static const char function_name[]="BoxDetect_SetForceOutBox";
static void log_flag(const char *message,const char *compact,uint32_t line,uint8_t flag)
{
    if (audio_log_level()&2u)
        audio_log_extended(3u,module,path,function_name,line,message,flag);
    if ((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x0c400000u,compact,compact,flag);
}

void audio_uart_case_force_out_4ac5a2(uint32_t value)
{
    uint8_t flag=(uint8_t)value;
    if (audio_uart_case_status_disabled==flag) {
        log_flag("force out box flag already %d",
                 "[box.detect]force out box flag already %d",0x195u,flag);
        return;
    }
    audio_uart_case_status_disabled=flag;
    log_flag("force out box flag set to %d",
             "[box.detect]force out box flag set to %d",0x19au,flag);
    audio_uart_case_force_out_apply_4ac798();
    audio_uart_case_display_refresh_4abf86();
    audio_uart_case_notify_4abec8();
    audio_uart_display_housekeep();
    if (flag!=0u)
        audio_uart_case_force_out_finish_4ac19c(0u);
}
