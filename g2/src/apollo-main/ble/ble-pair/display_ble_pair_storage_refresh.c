/* Native 0x4b4720 tail wrapper and AppDbReloadResolvingList 0x47b4d4. */
#include <stdint.h>
extern void DmPrivClearResList(void);
extern void audio_ble_subsystem_child_479418(void); /* selected AppLoadResList */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.smpdb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char function[]="AppDbReloadResolvingList";
#define LOG(line,plain,compact) do { \
 if(audio_log_flags()&2u)audio_log_extended(4u,module,path,function,line,plain); \
 if((audio_log_flags()&1u)||(audio_log_flags()&4u)) \
  (void)compressed_log_output(0x10000000u,compact,compact); \
} while(0)
/* Stock 0x47B4D4 (FUN_0047b4d4, AppDbReloadResolvingList) */
void audio_ble_pair_storage_refresh(void) {
    LOG(0x706u,
        "AppDbReloadResolvingList: Forcing reload of resolving list",
        "[ble.smpdb]AppDbReloadResolvingList: Forcing reload of resolving list");
    DmPrivClearResList();
    audio_ble_subsystem_child_479418();
    LOG(0x70eu,
        "AppDbReloadResolvingList: Resolving list reloaded",
        "[ble.smpdb]AppDbReloadResolvingList: Resolving list reloaded");
}
