/* Native 0x52fb58 one-time firmware image initialization gate. */
#include <stdint.h>
extern uint32_t audio_ble_radio_image_load_52f442(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="srv.em9305";
static const char source_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\DFU\\service_em9305_dfu.c";
static const char function[]="SVC_Em9305FwInit";
static const char fail[]="Failed to parse BLE firmware bin file";
static const char fail_compact[]="[srv.em9305]Failed to parse BLE firmware bin file";
static const char success[]="BLE firmware loaded from file successfully";
static const char success_compact[]="[srv.em9305]BLE firmware loaded from file successfully";
#define ACTIVE (*(volatile uint8_t *)(uintptr_t)0x20075016u)
uint32_t audio_ble_hci_radio_recover_52fb58(void) {
    if(ACTIVE!=0u) return 1u;
    if(audio_ble_radio_image_load_52f442()==0u) {
        if(audio_log_flags()&2u)
            audio_log_extended(1u,module,source_path,function,0x151u,fail);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x04000000u,fail_compact,fail_compact);
        return 0u;
    }
    ACTIVE=1u;
    if(audio_log_flags()&2u)
        audio_log_extended(4u,module,source_path,function,0x156u,success);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x10000000u,success_compact,success_compact);
    return 1u;
}
