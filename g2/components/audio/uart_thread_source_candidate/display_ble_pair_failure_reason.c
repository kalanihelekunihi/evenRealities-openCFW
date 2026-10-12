/* Native pairing reason formatter 0x4b8390 and status-five cleanup 0x4b46ce. */
#include <stdint.h>
extern void audio_ble_privacy_reset_local(void); /* 0x47acf8 */
extern void DmPrivClearResList(void);
extern uint8_t audio_ble_subsystem_link_state_200719c8[]; /* live RAM */
void audio_ble_pair_failure_reset(void) {
    audio_ble_privacy_reset_local();
    DmPrivClearResList();
    audio_ble_subsystem_link_state_200719c8[0x74u]=0u;
    for(uint32_t i=0u;i<4u;i++)audio_ble_subsystem_link_state_200719c8[0x70u+i]=0u;
    audio_ble_subsystem_link_state_200719c8[0x6cu]=0u;
}
const char *audio_ble_pair_failure_reason(uint8_t code) {
    switch(code) {
    case 1u:return "Passkey entry failed";
    case 2u:return "OOB not available";
    case 3u:return "Authentication requirements not met";
    case 4u:return "Confirm value failed";
    case 5u:audio_ble_pair_failure_reset();return "Pairing not supported by device";
    case 6u:return "Encryption key size not sufficient";
    case 7u:return "Command not supported";
    case 8u:return "Unspecified reason";
    case 9u:return "Repeated attempts";
    case 10u:return "Invalid parameters";
    case 11u:return "DH key check failed";
    case 12u:return "Numeric comparison failed";
    case 13u:return "BR/EDR pairing in progress";
    case 14u:return "Cross-transport key derivation not allowed";
    case 0xe1u:return "Transaction timeout";
    default:return "Unknown error";
    }
}
