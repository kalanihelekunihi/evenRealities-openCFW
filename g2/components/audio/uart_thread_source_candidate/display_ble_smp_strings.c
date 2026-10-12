/* Native smpEventStr 0x56d31e and smpStateStr 0x56d454.
 * Event literals are authenticated at stock pointer cells 0x56d844..bc. */
#include <stdint.h>
extern uint8_t audio_ble_smp_handler_state[];
extern const char *smprStateStr(uint8_t);
extern const char *smpiStateStr(uint8_t);
const char *smpEventStr(uint8_t event){
    static const char *const names[32]={
        [1]="API_PAIR_REQ",[2]="API_PAIR_RSP",[3]="API_CANCEL_REQ",
        [4]="API_AUTH_RSP",[5]="API_SECURITY_REQ",[6]="CMD_PKT",
        [7]="CMD_PAIRING_FAILED",[8]="DM_ENCRYPT_CMPL",[9]="DM_ENCRYPT_FAILED",
        [10]="DM_CONN_CLOSE",[11]="WSF_AES_CMPL",[12]="INT_SEND_NEXT_KEY",
        [13]="INT_MAX_ATTEMPTS",[14]="INT_PAIRING_CMPL",[15]="INT_RSP_TIMEOUT",
        [16]="INT_WI_TIMEOUT",[17]="INT_LESC",[18]="INT_LEGACY",
        [19]="INT_JW_NC",[20]="INT_PASSKEY",[21]="INT_OOB",
        [22]="API_USER_CONFIRM",[23]="API_USER_KEYPRESS",[24]="API_KEYPRESS_CMPL",
        [25]="WSF_ECC_CMPL",[26]="INT_PK_NEXT",[27]="INT_PK_CMPL",
        [28]="WSF_CMAC_CMPL",[29]="DH_CHECK_FAILURE",[31]="INT_CLEANUP"
    };
    return event<32u&&names[event]!=0?names[event]:"Unknown";
}
const char *smpStateStr(uint8_t state){
    return audio_ble_smp_handler_state[0x3au]==0u?smprStateStr(state):smpiStateStr(state);
}
