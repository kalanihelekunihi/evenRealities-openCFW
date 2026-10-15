/* Apollo appMasterResolvedAddrInd, native 0x50393e. */
#include <stdint.h>

extern volatile uint8_t audio_ble_subsystem_state_20071670[];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint32_t audio_ble_master_resolution_check_47ab6c(const uint8_t *,uint16_t);

static const char module[]="ble.master";
static const char source[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_master.c";
static const char function[]="appMasterResolvedAddrInd";
static const char idle[]="appMasterResolvedAddrInd: Address resolution not in progress, ignoring result";
static const char idle_short[]="[ble.master]appMasterResolvedAddrInd: Address resolution not in progress, ignoring result";
static const char result[]="appMasterResolvedAddrInd: Address resolution result, status: 0x%02X";
static const char result_short[]="[ble.master]appMasterResolvedAddrInd: Address resolution result, status: 0x%02X";
static const char resolved[]="appMasterResolvedAddrInd: RPA resolved successfully, record index: %d";
static const char resolved_short[]="[ble.master]appMasterResolvedAddrInd: RPA resolved successfully, record index: %d";
static const char connected[]="appMasterResolvedAddrInd: Connection established successfully";
static const char connected_short[]="[ble.master]appMasterResolvedAddrInd: Connection established successfully";
static const char failed[]="appMasterResolvedAddrInd: Failed to establish connection";
static const char failed_short[]="[ble.master]appMasterResolvedAddrInd: Failed to establish connection";
static const char unresolved[]="appMasterResolvedAddrInd: RPA resolution failed, status: 0x%02X";
static const char unresolved_short[]="[ble.master]appMasterResolvedAddrInd: RPA resolution failed, status: 0x%02X";

#define LOG(level,line,plain,compact,mask,...) do {                       \
    if (audio_log_flags()&2u)                                             \
        audio_log_extended(level,module,source,function,line,plain,      \
                           ##__VA_ARGS__);                               \
    if ((audio_log_flags()&1u)||(audio_log_flags()&4u))                   \
        (void)compressed_log_output(mask,compact,compact,##__VA_ARGS__); \
} while (0)

void audio_ble_master_event_50393e(void *event,void *record)
{
    (void)record;
    const uint8_t *message=(const uint8_t *)event;
    uint16_t handle=(uint16_t)message[0]|((uint16_t)message[1]<<8u);
    uint8_t status=message[3];
    if (audio_ble_subsystem_state_20071670[0x9cu]==0u) {
        LOG(2u,0x24au,idle,idle_short,0x08000000u);
        return;
    }
    LOG(4u,0x24eu,result,result_short,0x10400000u,status);
    uint8_t index=audio_ble_subsystem_state_20071670[0x97u];
    if (status==0u) {
        LOG(4u,0x256u,resolved,resolved_short,0x10400000u,handle);
        if (audio_ble_master_resolution_check_47ab6c(
              (const uint8_t *)audio_ble_subsystem_state_20071670+
              (uint32_t)index*15u,handle)!=0u) {
            LOG(4u,0x25bu,connected,connected_short,0x10000000u);
        } else {
            LOG(2u,0x25fu,failed,failed_short,0x08000000u);
        }
    } else {
        LOG(2u,0x264u,unresolved,unresolved_short,0x08400000u,status);
    }
    audio_ble_subsystem_state_20071670[0x9cu]=0u;
}
