/* Native OTA_FileSystemSetBootloaderFlag 0x478860. */
#include <stdint.h>
extern volatile uint32_t audio_ble_bootloader_flag; /* flash mapped 0x007fe000 */
extern const uint8_t audio_ble_ota_flag_seed[16]; /* ROM 0x784ed0 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439c04 */
extern void audio_dump_hex(const char *,uint32_t,const uint8_t *,uint32_t); /* 0x43dacc */
extern uint32_t g2_gpio_critical_save(void); /* 0x473940 */
extern int32_t audio_ble_nvm_write_words(uint32_t,const uint8_t *,uint8_t *,uint32_t); /* 0x4d0a2c */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.smpdb";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char function[]="OTA_FileSystemSetBootloaderFlag";
/* Stock 0x478860 (OTA_FileSystemSetBootloaderFlag; TSV FUN_00478860) */
void audio_ble_ota_export_mode_set(uint32_t requested) {
    volatile uint32_t *flag=&audio_ble_bootloader_flag;
    uint32_t previous=*flag;
    if(audio_log_level()&2u)
      audio_log_extended(4u,module,source,function,0x98u,
        "OTA_FileSystemSetBootloaderFlag: 0x%x, 0x%x",previous,requested);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
      (void)compressed_log_output(0x10800000u,
        "[ble.smpdb]OTA_FileSystemSetBootloaderFlag: 0x%x, 0x%x",
        "[ble.smpdb]OTA_FileSystemSetBootloaderFlag: 0x%x, 0x%x",previous,requested);
    audio_dump_hex("ota flag",16u,(const uint8_t *)(const void *)flag,32u);
    if(requested==previous) return;
    uint32_t page[4];
    (void)audio_queue_copy_bytes(page,audio_ble_ota_flag_seed,16u);
    page[0]=requested;
    if(audio_log_level()&2u)
      audio_log_extended(4u,module,source,function,0x9fu,
        "APP will write value at 0x%x: 0x%x",(uint32_t)(uintptr_t)flag,requested);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
      (void)compressed_log_output(0x10800000u,
        "[ble.smpdb]APP will write value at 0x%x: 0x%x",
        "[ble.smpdb]APP will write value at 0x%x: 0x%x",(uint32_t)(uintptr_t)flag,requested);
    uint32_t prior=g2_gpio_critical_save();
    int32_t result=audio_ble_nvm_write_words(0x12344321u,(const uint8_t *)page,(uint8_t *)(void *)flag,4u);
    __asm volatile("msr primask, %0" : : "r"(prior) : "memory");
    if(result!=0) {
      if(audio_log_level()&2u)
        audio_log_extended(1u,module,source,function,0xa9u,
          "Flash program failed: return code = 0x%x",result);
      if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x04400000u,
          "[ble.smpdb]Flash program failed: return code = 0x%x",
          "[ble.smpdb]Flash program failed: return code = 0x%x",result);
    }
}
