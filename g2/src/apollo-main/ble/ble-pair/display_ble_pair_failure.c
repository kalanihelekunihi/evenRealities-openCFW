/* Native AppDbHandlePairingFailure 0x47c568. */
#include <stdint.h>
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_ble_pair_failure_prepare(void); /* 0x47c2bc */
extern uint8_t *audio_ble_pair_record(uint8_t); /* 0x4bb07c */
extern void audio_ble_pair_failure_clear(uint8_t); /* 0x47c8cc */
static const char module[]="ble.smpdb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char function[]="AppDbHandlePairingFailure";
#define LOG(level,line,mask,plain,compact,...) do { \
 if(audio_log_flags()&2u)audio_log_extended(level,module,path,function,line,plain,##__VA_ARGS__); \
 if((audio_log_flags()&1u)||(audio_log_flags()&4u)) \
  (void)compressed_log_output(mask,compact,compact,##__VA_ARGS__); \
} while(0)
/* Stock 0x47C568 (FUN_0047c568, AppDbHandlePairingFailure) */
void audio_ble_pair_failure(uint8_t conn,uint8_t status) {
    LOG(4u,0x872u,0x10800000u,
        "AppDbHandlePairingFailure: Processing pairing failure for connId=%d, status=0x%02x",
        "[ble.smpdb]AppDbHandlePairingFailure: Processing pairing failure for connId=%d, status=0x%02x",
        conn,status);
    audio_ble_pair_failure_prepare();
    uint8_t *record=audio_ble_pair_record(conn);
    if(!record) {
        LOG(4u,0x8a6u,0x10400000u,
            "AppDbHandlePairingFailure: No database handle found for connection %d - no action needed",
            "[ble.smpdb]AppDbHandlePairingFailure: No database handle found for connection %d - no action needed",conn);
        return;
    }
    if(!record[0x30u]||(record[0x2eu]&5u)==0u) {
        LOG(4u,0x89fu,0x10c00000u,
            "AppDbHandlePairingFailure: No valid pairing record to clear for connection %d (valid=%d, keyMask=0x%02x)",
            "[ble.smpdb]AppDbHandlePairingFailure: No valid pairing record to clear for connection %d (valid=%d, keyMask=0x%02x)",
            conn,record[0x30u],record[0x2eu]);
        record[0x30u]=0u;record[0x2fu]=0u;
        return;
    }
    LOG(2u,0x880u,0x09800000u,
        "AppDbHandlePairingFailure: Clearing valid pairing record for device %02X:%02X:%02X:%02X:%02X:%02X",
        "[ble.smpdb]AppDbHandlePairingFailure: Clearing valid pairing record for device %02X:%02X:%02X:%02X:%02X:%02X",
        record[5],record[4],record[3],record[2],record[1],record[0]);
    switch(status) {
    case 1u:
        LOG(2u,0x88eu,0x08000000u,
            "AppDbHandlePairingFailure: Passkey entry failed - clearing record",
            "[ble.smpdb]AppDbHandlePairingFailure: Passkey entry failed - clearing record");break;
    case 3u:
        LOG(2u,0x892u,0x08000000u,
            "AppDbHandlePairingFailure: Authentication requirements not met - clearing record",
            "[ble.smpdb]AppDbHandlePairingFailure: Authentication requirements not met - clearing record");break;
    case 4u:
        LOG(2u,0x88au,0x08000000u,
            "AppDbHandlePairingFailure: Confirm value failed - clearing record",
            "[ble.smpdb]AppDbHandlePairingFailure: Confirm value failed - clearing record");break;
    case 11u:
        LOG(1u,0x885u,0x04000000u,
            "AppDbHandlePairingFailure: DH Key Check failed - this may indicate corrupted data",
            "[ble.smpdb]AppDbHandlePairingFailure: DH Key Check failed - this may indicate corrupted data");break;
    default:
        LOG(2u,0x896u,0x08400000u,
            "AppDbHandlePairingFailure: Unknown failure reason (0x%02x) - clearing record",
            "[ble.smpdb]AppDbHandlePairingFailure: Unknown failure reason (0x%02x) - clearing record",status);break;
    }
    audio_ble_pair_failure_clear(conn);
}
