/* Connection control block reset placed at the end of the stock Cordio
 * dm_conn.c object (after DmConnRole 0x4B73C4), native 0x4B73E8..0x4B7425.
 *
 * Neither public r20.05c nor AmbiqSuite R3.2.0 dm_conn.c has this function; it
 * is a product/Ambiq-family addition called only by appBleStart 0x4B80F0
 * (0x4B80F2). It clears all DM_CONN_MAX (3) dmConnCcb_t records and leaves
 * each one free with no HCI handle and no role. */
#include <stdint.h>

extern uint8_t audio_dm_connection_records[]; /* dmConnCb.ccb[3], RAM 0x200712A4, 3 x 0x30 */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* memset(p, n, c) 0x43c0e4 */

/* dmConnCcb_t (Ambiq layout, 0x30 bytes) */
#define G2_CCB_SIZE              0x30u
#define G2_CCB_HANDLE            0x0Cu /* uint16_t handle */
#define G2_CCB_CONN_ID           0x10u /* dmConnId_t connId */
#define G2_CCB_UPDATING          0x11u /* bool_t updating */
#define G2_CCB_IN_USE            0x16u /* uint8_t inUse */
#define G2_CCB_ROLE              0x19u /* uint8_t role */
#define G2_CCB_FEATURES_PRESENT  0x2Cu /* bool_t featuresPresent */

void vendorCcbInitLike(void)
{
    uint8_t *ccb = audio_dm_connection_records;

    for (uint8_t i = 0u; i < 3u; i++) {
        audio_uart_buffer_zero(ccb, G2_CCB_SIZE, 0u);
        *(uint16_t *)(void *)(ccb + G2_CCB_HANDLE) = 0xFFFFu; /* DM_CONN_HCI_HANDLE_NONE */
        ccb[G2_CCB_CONN_ID] = 0u;
        ccb[G2_CCB_UPDATING] = 0u;
        ccb[G2_CCB_IN_USE] = 0u;
        ccb[G2_CCB_FEATURES_PRESENT] = 0u;
        ccb[G2_CCB_ROLE] = 0xFFu;
        ccb += G2_CCB_SIZE;
    }
}
