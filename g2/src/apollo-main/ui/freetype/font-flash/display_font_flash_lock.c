/* Native MX25U flash lock/power wrappers 0x46f65e and 0x46f674. */
#include <stdint.h>
extern int32_t audio_file_mutex_acquire(void *,uint32_t); /* selected osMutexAcquire 0x4497b6 */
extern int32_t audio_file_mutex_release(void *); /* selected osMutexRelease 0x44981c */
extern int32_t audio_uart_font_flash_power(void *,uint8_t,uint8_t); /* 0x4c26e0 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void *audio_uart_font_flash_device; /* RAM0x20074544 */
extern void *audio_uart_font_flash_mutex; /* RAM0x20074548 */
extern uint8_t audio_uart_font_flash_sleep; /* RAM0x20074fb9 */
extern uint8_t audio_uart_font_flash_mode; /* RAM0x20074fb8 */
static const char module[]="drv.norflash"; /* ROM0x785cd0 */
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c"; /* ROM0x70258c */
static const char lock_fn[]="mspi_flash_mutex_lock"; /* ROM0x776ea4 */
static const char unlock_fn[]="mspi_flash_mutex_unlock"; /* ROM0x776ebc */
static const char lock_error[]="[mspi_flash_mutex_id] lock timeout"; /* ROM0x753e28 */
static const char unlock_error[]="[mspi_flash_mutex_id] unlock timeout"; /* ROM0x749a74 */
static const char lock_short[]="[drv.norflash][mspi_flash_mutex_id] lock timeout"; /* ROM0x729114 */
static const char unlock_short[]="[drv.norflash][mspi_flash_mutex_id] unlock timeout"; /* ROM0x729148 */
void audio_uart_brightness_stage_46f5a6(void) {
    if(audio_uart_font_flash_mutex==0) return;
    if(audio_file_mutex_acquire(audio_uart_font_flash_mutex,UINT32_MAX)==0) return;
    if(audio_log_flags()&2u)
        audio_log_extended(1u,module,source,lock_fn,0xc3u,lock_error);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x04000000u,lock_short,lock_short);
}
void audio_uart_brightness_commit_46f604(void) {
    if(audio_uart_font_flash_mutex==0) return;
    if(audio_file_mutex_release(audio_uart_font_flash_mutex)==0) return;
    if(audio_log_flags()&2u)
        audio_log_extended(1u,module,source,unlock_fn,0xccu,unlock_error);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x04000000u,unlock_short,unlock_short);
}
void audio_uart_ring_config_lock(void) {
    audio_uart_brightness_stage_46f5a6();
    if(audio_uart_font_flash_mode!=1u) {
        (void)audio_uart_font_flash_power(audio_uart_font_flash_device,0u,1u);
        audio_uart_font_flash_sleep=0u;
    }
}
void audio_uart_ring_config_unlock(void) {
    if(audio_uart_font_flash_mode!=1u&&audio_uart_font_flash_sleep!=1u) {
        (void)audio_uart_font_flash_power(audio_uart_font_flash_device,2u,1u);
        audio_uart_font_flash_sleep=1u;
    }
    audio_uart_brightness_commit_46f604();
}
