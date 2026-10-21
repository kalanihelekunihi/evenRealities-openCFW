/* Cordio AppDbHandleResolvedAddr, native Apollo 0x47ab6c. */
#include <stdint.h>

extern uint8_t audio_ble_dm_conn_state_table_20067a30[];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="ble.smpdb";
static const char source[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char function[]="AppDbHandleResolvedAddr";
static const char invalid[]="AppDbHandleResolvedAddr: Invalid record index or record";
static const char invalid_short[]="[ble.smpdb]AppDbHandleResolvedAddr: Invalid record index or record";
static const char success[]="AppDbHandleResolvedAddr: Address resolved successfully, public address of record[%d] is %02X:%02X:%02X:%02X:%02X:%02X";
static const char success_short[]="[ble.smpdb]AppDbHandleResolvedAddr: Address resolved successfully, public address of record[%d] is %02X:%02X:%02X:%02X:%02X:%02X";
static const char valid[]="AppDbHandleResolvedAddr: Found valid LTK, can establish encrypted connection";
static const char valid_short[]="[ble.smpdb]AppDbHandleResolvedAddr: Found valid LTK, can establish encrypted connection";
static const char missing[]="AppDbHandleResolvedAddr: No valid LTK found, cannot establish encrypted connection";
static const char missing_short[]="[ble.smpdb]AppDbHandleResolvedAddr: No valid LTK found, cannot establish encrypted connection";

#define LOG(level,line,plain,compact,mask,...) do {                       \
    if (audio_log_flags()&2u)                                             \
        audio_log_extended(level,module,source,function,line,plain,      \
                           ##__VA_ARGS__);                               \
    if ((audio_log_flags()&1u)||(audio_log_flags()&4u))                   \
        (void)compressed_log_output(mask,compact,compact,##__VA_ARGS__); \
} while (0)

uint32_t audio_ble_master_resolution_check_47ab6c(const uint8_t *address,
                                                     uint16_t index)
{
    const uint8_t *row=audio_ble_dm_conn_state_table_20067a30+
                       (uint32_t)index*200u;
    if (index>=10u || row[0x2fu]==0u || row[0x30u]==0u) {
        LOG(1u,0x435u,invalid,invalid_short,0x04000000u);
        return 0u;
    }
    LOG(4u,0x43bu,success,success_short,0x11c00000u,index,
        address[5],address[4],address[3],address[2],address[1],address[0]);
    if ((row[0x2eu]&1u)!=0u) {
        LOG(4u,0x440u,valid,valid_short,0x10000000u);
        return 1u;
    }
    LOG(2u,0x449u,missing,missing_short,0x08000000u);
    return 0u;
}
