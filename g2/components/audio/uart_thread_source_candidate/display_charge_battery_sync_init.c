/* Native CHG_InitBatterySync 0x4acf7c. Product RAM retains explicit placement. */
#include <stdint.h>
extern void *audio_charge_sync_mutex; /* RAM 0x20074370 */
extern uint8_t audio_charge_sync_record[24u]; /* RAM 0x20073b30 */
extern uint8_t audio_charge_sync_peer_record[8u]; /* RAM 0x20074104 */
extern volatile uint8_t audio_charge_sync_flag_20074f97;
extern volatile uint8_t audio_charge_sync_flag_20074f98;
extern volatile uint16_t audio_charge_sync_mode_20074f1a;
extern volatile uint16_t audio_charge_sync_phase_20074f1c;
extern volatile uint8_t audio_charge_sync_flag_20074f99;
extern void *audio_uart_mutex_new(const void *); /* selected osMutexNew 0x44971c */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern void audio_settings_init_battery_callbacks(void); /* selected 0x4aea40 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="charger_common";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\charger\\charger_common.c";
static const char function[]="CHG_InitBatterySync";
#define LOG(level,line,mask,plain,compact) do { \
 if(audio_log_level()&2u)audio_log_extended(level,module,path,function,line,plain); \
 if((audio_log_level()&1u)||(audio_log_level()&4u)) \
  (void)compressed_log_output(mask,compact,compact); \
} while(0)
void audio_device_manager_battery_sync_init(void) {
    LOG(4u,0x68u,0x10000000u,"CHG_InitBatterySync",
        "[charger_common]CHG_InitBatterySync");
    audio_charge_sync_mutex=audio_uart_mutex_new(0);
    if(audio_charge_sync_mutex==0) {
        LOG(1u,0x6du,0x04000000u,"Failed to create sync battery mutex",
            "[charger_common]Failed to create sync battery mutex");
        return;
    }
    audio_uart_buffer_zero(audio_charge_sync_record,24u,0u);
    audio_uart_buffer_zero(audio_charge_sync_peer_record,8u,0u);
    *(uint32_t *)(void *)audio_charge_sync_peer_record=UINT32_MAX;
    *(uint32_t *)(void *)(audio_charge_sync_record+16u)=UINT32_MAX;
    audio_charge_sync_flag_20074f97=0u;
    audio_charge_sync_flag_20074f98=1u;
    audio_charge_sync_mode_20074f1a=0u;
    audio_charge_sync_phase_20074f1c=2u;
    audio_charge_sync_flag_20074f99=0u;
    audio_settings_init_battery_callbacks();
}
