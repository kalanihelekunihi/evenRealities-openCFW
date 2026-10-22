/* Packetcraft Cordio ATT server, attsProcMtuReq() stock variant.
 * Stock source: D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\
 *               ble-host\sources\stack\att\atts_proc.c (product-modified;
 *               its ATT_TRACE_WARN1 sits at line 255, upstream r20.05c 249)
 * Native 0x56c6fc..0x56c924; literal pool 0x56cd9c..0x56cdbc.
 *
 * Differences from upstream r20.05c / AmbiqSuite R3.2.0:
 *  - the peer MTU floor is 247 (0xf7) instead of ATT_DEFAULT_MTU (23), so a
 *    smaller client MTU is recorded as 247;
 *  - an extra product elog line 0x115 "attsProcMtuReq mtu %d localMtu %d"
 *    (tag atts.proc) plus its compressed-log copy;
 *  - ATT_TRACE_WARN1 expands to the product WSF-trace -> elog dispatch
 *    (level picked by comparing the level label, raw WsfTrace fallback when
 *    elog is not up, HCI-tag suppression), as elsewhere in the G2 Cordio
 *    build. */
#include <stdint.h>

#define ATT_PDU_MTU_REQ 0x02u
#define ATT_PDU_MTU_RSP 0x03u
#define ATT_ERR_NOT_SUP 0x06u
#define ATTS_CSF_EATT_BEARER 0x02u /* features bit 1 */
#define G2_ATT_MIN_PEER_MTU 0xf7u   /* product floor; upstream ATT_DEFAULT_MTU 23 */
#define L2C_PAYLOAD_START 8u
#define ATT_HDR_LEN 1u
#define ATT_MTU_RSP_LEN 3u
#define L2C_HDR_LEN 4u

/* attsCcb_t fields used here. */
typedef struct {
    uint8_t opaque0[0x10];
    uint8_t *main_ccb; /* +0x10 pMainCcb */
    uint8_t opaque1[0x24 - 0x14];
    uint8_t conn_id;   /* +0x24 connId */
    uint8_t slot;      /* +0x25 slot */
} g2_atts_ccb_view_t;

/* attCfg_t fields used here. */
typedef struct {
    uint16_t trans_timeout; /* +0x0 transTimeout */
    uint16_t pad;
    uint16_t mtu;           /* +0x4 */
} g2_att_cfg_view_t;

extern const g2_att_cfg_view_t *pAttCfg; /* RAM 0x200004b4 (Cordio pAttCfg) */

extern void AttsCsfGetFeatures(uint8_t conn_id, uint8_t *features, uint8_t length);
extern uint16_t HciGetMaxRxAclLen(void);
extern uint8_t *attMsgAlloc(uint16_t length);
extern void attL2cDataReq(uint8_t *ccb, uint8_t slot, uint16_t length, uint8_t *packet);
extern void attSetMtu(uint8_t *ccb, uint8_t slot, uint16_t peer_mtu, uint16_t local_mtu);
extern void attsErrRsp(uint8_t *ccb, uint8_t slot, uint8_t opcode, uint16_t handle, uint8_t error);

extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *a, const char *b, uint32_t count); /* 0x44b610 */
extern void audio_ble_wsf_trace(const char *level, ...);                      /* WsfTrace 0x52a63c */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t level, const char *tag, const char *path, const char *function,
                               uint32_t line, const char *format, ...);
extern uint32_t compressed_log_output(uint32_t id, const char *format, const char *copy, ...);

static const char s_err[] = "ERR";   /* ROM 0x56c924 */
static const char s_warn[] = "WARN"; /* ROM 0x78cccc */
static const char s_info[] = "INFO"; /* ROM 0x78ccd4 */
static const char s_att[] = "ATT";   /* ROM 0x56c928 */
static const char s_hci[] = "HCI";   /* ROM 0x56c92c */
static const char s_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\atts_proc.c"; /* ROM 0x6dca54 */
static const char s_function[] = "attsProcMtuReq";                          /* ROM 0x785300 */
static const char s_features[] = "attsProcMtuReq features 0x%02x";          /* ROM 0x75e2f0 */
static const char s_proc_tag[] = "atts.proc";                               /* ROM 0x78a460 */
static const char s_mtu[] = "attsProcMtuReq mtu %d localMtu %d";            /* ROM 0x7524fc */
static const char s_mtu_c[] = "[atts.proc]attsProcMtuReq mtu %d localMtu %d"; /* ROM 0x731c64 */

/* Product WSF trace macro: elog level 1..4 chosen by the level label, or the
 * raw WsfTrace when elog is not enabled (HCI-tagged traces suppressed). */
#define G2_WSF_TRACE(label, tag, line, ...)                                                    \
    do {                                                                                       \
        if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||                                 \
            audio_l2c_strncmp((label), s_err, 3u) != 0) {                                      \
            if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||                             \
                audio_l2c_strncmp((label), s_warn, 4u) != 0) {                                 \
                if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||                         \
                    audio_l2c_strncmp((label), s_info, 4u) != 0) {                             \
                    if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u) {                     \
                        if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||                 \
                            audio_l2c_strncmp((tag), s_hci, 3u) != 0)                          \
                            audio_ble_wsf_trace((label), __VA_ARGS__);                         \
                    } else if ((audio_log_flags() & 2u) != 0u) {                               \
                        audio_log_extended(4u, (tag), s_path, s_function, (line), __VA_ARGS__);\
                    }                                                                          \
                } else if ((audio_log_flags() & 2u) != 0u) {                                   \
                    audio_log_extended(3u, (tag), s_path, s_function, (line), __VA_ARGS__);    \
                }                                                                              \
            } else if ((audio_log_flags() & 2u) != 0u) {                                       \
                audio_log_extended(2u, (tag), s_path, s_function, (line), __VA_ARGS__);        \
            }                                                                                  \
        } else if ((audio_log_flags() & 2u) != 0u) {                                           \
            audio_log_extended(1u, (tag), s_path, s_function, (line), __VA_ARGS__);            \
        }                                                                                      \
    } while (0)

void attsProcMtuReq_56c6fc(void *ccb, uint16_t len, uint8_t *packet)
{
    g2_atts_ccb_view_t *pCcb = (g2_atts_ccb_view_t *)ccb;
    uint8_t features;
    (void)len;

    AttsCsfGetFeatures(pCcb->conn_id, &features, sizeof features);
    G2_WSF_TRACE(s_warn, s_att, 0xffu, s_features, features);

    if ((features & ATTS_CSF_EATT_BEARER) != 0u) {
        attsErrRsp(pCcb->main_ccb, pCcb->slot, ATT_PDU_MTU_REQ, 0u, ATT_ERR_NOT_SUP);
        return;
    }

    const uint8_t *p = packet + L2C_PAYLOAD_START + ATT_HDR_LEN;
    uint16_t mtu = (uint16_t)(p[0] | ((uint16_t)p[1] << 8));
    if (mtu < G2_ATT_MIN_PEER_MTU)
        mtu = G2_ATT_MIN_PEER_MTU;

    /* WSF_MIN evaluates HciGetMaxRxAclLen() twice, as upstream. */
    uint16_t local_mtu = ((int32_t)pAttCfg->mtu < (int32_t)HciGetMaxRxAclLen() - (int32_t)L2C_HDR_LEN)
                             ? pAttCfg->mtu
                             : (uint16_t)(HciGetMaxRxAclLen() - L2C_HDR_LEN);

    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, s_proc_tag, s_path, s_function, 0x115u, s_mtu, mtu, local_mtu);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10800000u, s_mtu_c, s_mtu_c, mtu, local_mtu);

    uint8_t *rsp = attMsgAlloc(L2C_PAYLOAD_START + ATT_MTU_RSP_LEN);
    if (rsp != 0) {
        uint8_t *q = rsp + L2C_PAYLOAD_START;
        q[0] = ATT_PDU_MTU_RSP;
        q[1] = (uint8_t)local_mtu;
        q[2] = (uint8_t)(local_mtu >> 8);
        attL2cDataReq(pCcb->main_ccb, pCcb->slot, ATT_MTU_RSP_LEN, rsp);
    }
    attSetMtu(pCcb->main_ccb, pCcb->slot, mtu, local_mtu);
}
