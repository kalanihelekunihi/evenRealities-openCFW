/* Native SVC_ANCC_GetNotifCount 0x4974d4. */
#include <stdint.h>
extern void *audio_settings_ancc_mutex; /* RAM 0x2007491c */
extern uint8_t audio_settings_ancc_count; /* RAM 0x2007500d */
extern int32_t audio_file_mutex_acquire(void *,uint32_t); /* selected 0x4497b6 */
extern int32_t audio_file_mutex_release(void *); /* selected 0x44981c */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="svc.ancc";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\message_notify\\service_ancc.c";
static const char function[]="SVC_ANCC_GetNotifCount";
static const char no_mutex[]="ANCC message mutex not initialized";
static const char no_mutex_short[]="[svc.ancc]ANCC message mutex not initialized";
static const char acquire_fail[]="Failed to acquire ANCC message mutex during get count";
static const char acquire_fail_short[]="[svc.ancc]Failed to acquire ANCC message mutex during get count";
uint32_t audio_settings_unread_message_count(void) {
    void *mutex=audio_settings_ancc_mutex;
    if(mutex==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,176u,no_mutex);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,no_mutex_short,no_mutex_short);
        return 0u;
    }
    if(audio_file_mutex_acquire(mutex,UINT32_MAX)!=0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,181u,acquire_fail);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,acquire_fail_short,acquire_fail_short);
        return 0u;
    }
    uint32_t count=audio_settings_ancc_count;
    (void)audio_file_mutex_release(mutex);
    return count;
}
