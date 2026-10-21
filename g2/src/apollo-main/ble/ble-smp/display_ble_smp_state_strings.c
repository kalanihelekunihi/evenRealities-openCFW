/* Native smpiStateStr 0x537f24 and smprStateStr 0x538114.
 * Literals are exact authenticated stock pointer cells, not executable bytes. */
#include <stdint.h>
const char *smpiStateStr(uint8_t state){
    static const char *const names[]={
        "I_IDLE", /* 0x00: stock pointer cell 0x538040 */
        "I_PAIR_RSP", /* 0x01: stock pointer cell 0x538044 */
        "I_MODE_SELECT", /* 0x02: stock pointer cell 0x538048 */
        "I_LESC_PIN", /* 0x03: stock pointer cell 0x53804c */
        "I_PUB_KEY", /* 0x04: stock pointer cell 0x538050 */
        "I_AUTH_SELECT", /* 0x05: stock pointer cell 0x538054 */
        "I_JWNC_WAIT_CNF", /* 0x06: stock pointer cell 0x538058 */
        "I_JWNC_RAND", /* 0x07: stock pointer cell 0x53805c */
        "I_JWNC_CHECK_1", /* 0x08: stock pointer cell 0x538060 */
        "I_JWNC_CHECK_2", /* 0x09: stock pointer cell 0x538064 */
        "I_JWNC_WAIT_USER", /* 0x0a: stock pointer cell 0x538068 */
        "I_PK_KEYPRESS", /* 0x0b: stock pointer cell 0x53806c */
        "I_PK_CALC", /* 0x0c: stock pointer cell 0x538070 */
        "I_PK_CNF", /* 0x0d: stock pointer cell 0x538074 */
        "I_PK_RAND", /* 0x0e: stock pointer cell 0x538078 */
        "I_PK_CHECK", /* 0x0f: stock pointer cell 0x53807c */
        "I_PK_REPEAT", /* 0x10: stock pointer cell 0x538080 */
        "I_OOB_SEND_RAND", /* 0x11: stock pointer cell 0x538084 */
        "I_OOB_WAIT_RAND", /* 0x12: stock pointer cell 0x538088 */
        "I_CALC_DHKEY", /* 0x13: stock pointer cell 0x53808c */
        "I_CALC_F5_TKEY", /* 0x14: stock pointer cell 0x538090 */
        "I_CALC_F5_MACKEY", /* 0x15: stock pointer cell 0x538094 */
        "I_CALC_F5_LTK", /* 0x16: stock pointer cell 0x538098 */
        "I_CALC_F6_EA", /* 0x17: stock pointer cell 0x53809c */
        "I_CALC_F6_EB", /* 0x18: stock pointer cell 0x5380a0 */
        "I_VERIFY_DH_CHECK", /* 0x19: stock pointer cell 0x5380a4 */
        "I_LEGACY_PIN", /* 0x1a: stock pointer cell 0x5380a8 */
        "I_CNF_CALC_1", /* 0x1b: stock pointer cell 0x5380ac */
        "I_CNF_CALC_2", /* 0x1c: stock pointer cell 0x5380b0 */
        "I_PAIR_CNF", /* 0x1d: stock pointer cell 0x5380b4 */
        "I_PAIR_RAND", /* 0x1e: stock pointer cell 0x5380b8 */
        "I_CNF_VER_CALC_1", /* 0x1f: stock pointer cell 0x5380bc */
        "I_CNF_VER_CALC_2", /* 0x20: stock pointer cell 0x5380c0 */
        "I_STK_CALC", /* 0x21: stock pointer cell 0x5380c4 */
        "I_ENCRYPT", /* 0x22: stock pointer cell 0x5380c8 */
        "I_KEY_DIST", /* 0x23: stock pointer cell 0x5380cc */
        "I_ATTEMPTS", /* 0x24: stock pointer cell 0x5380d0 */
        "I_RSP_TO", /* 0x25: stock pointer cell 0x5380d4 */
    };
    return state<38u?names[state]:"I_Unknown";
}
const char *smprStateStr(uint8_t state){
    static const char *const names[]={
        "R_IDLE", /* 0x00: stock pointer cell 0x538240 */
        "R_API_PAIR_REQ", /* 0x01: stock pointer cell 0x538244 */
        "R_API_PAIR_RSP", /* 0x02: stock pointer cell 0x538248 */
        "R_MODE_SELECT", /* 0x03: stock pointer cell 0x53824c */
        "R_PUB_KEY", /* 0x04: stock pointer cell 0x538250 */
        "R_LESC_PIN", /* 0x05: stock pointer cell 0x538254 */
        "R_AUTH_SELECT", /* 0x06: stock pointer cell 0x538258 */
        "R_JWNC_SETUP", /* 0x07: stock pointer cell 0x53825c */
        "R_JWNC_WAIT_RAND", /* 0x08: stock pointer cell 0x538260 */
        "R_JWNC_CALC_G2", /* 0x09: stock pointer cell 0x538264 */
        "R_JWNC_WAIT_USER", /* 0x0a: stock pointer cell 0x538268 */
        "R_JWNC_WAIT_USER_DH", /* 0x0b: stock pointer cell 0x53826c */
        "R_PK_KEYPRESS", /* 0x0c: stock pointer cell 0x538270 */
        "R_PK_WAIT_AUTH", /* 0x0d: stock pointer cell 0x538274 */
        "R_PK_WAIT_CNF", /* 0x0e: stock pointer cell 0x538278 */
        "R_PK_CALC", /* 0x0f: stock pointer cell 0x53827c */
        "R_PK_RAND", /* 0x10: stock pointer cell 0x538280 */
        "R_PK_CHECK", /* 0x11: stock pointer cell 0x538284 */
        "R_PK_REPEAT", /* 0x12: stock pointer cell 0x538288 */
        "R_OOB_SEND_RAND", /* 0x13: stock pointer cell 0x53828c */
        "R_OOB_WAIT_RAND", /* 0x14: stock pointer cell 0x538290 */
        "R_WAIT_DH_CHECK", /* 0x15: stock pointer cell 0x538294 */
        "R_CALC_DHKEY", /* 0x16: stock pointer cell 0x538298 */
        "R_CALC_F5_TKEY", /* 0x17: stock pointer cell 0x53829c */
        "R_CALC_F5_MACKEY", /* 0x18: stock pointer cell 0x5382a0 */
        "R_CALC_F5_LTK", /* 0x19: stock pointer cell 0x5382a4 */
        "R_CALC_F6_EA", /* 0x1a: stock pointer cell 0x5382a8 */
        "R_CALC_F6_EB", /* 0x1b: stock pointer cell 0x5382ac */
        "R_PIN_PAIR_1", /* 0x1c: stock pointer cell 0x5382b0 */
        "R_PIN_PAIR_2", /* 0x1d: stock pointer cell 0x5382b4 */
        "R_CNF_CALC_1", /* 0x1e: stock pointer cell 0x5382b8 */
        "R_CNF_CALC_2", /* 0x1f: stock pointer cell 0x5382bc */
        "R_PAIR_RAND", /* 0x20: stock pointer cell 0x5382c0 */
        "R_CNF_VER_CALC_1", /* 0x21: stock pointer cell 0x5382c4 */
        "R_CNF_VER_CALC_2", /* 0x22: stock pointer cell 0x5382c8 */
        "R_STK_CALC", /* 0x23: stock pointer cell 0x5382cc */
        "R_ENCRYPT", /* 0x24: stock pointer cell 0x5382d0 */
        "R_KEY_DIST", /* 0x25: stock pointer cell 0x5382d4 */
        "R_ATTEMPTS", /* 0x26: stock pointer cell 0x5382d8 */
        "R_RSP_TO", /* 0x27: stock pointer cell 0x5382dc */
    };
    return state<40u?names[state]:"R_Unknown";
}
