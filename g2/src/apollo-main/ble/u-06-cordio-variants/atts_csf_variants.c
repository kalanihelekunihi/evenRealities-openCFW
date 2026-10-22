/* Stock source: D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-host\sources\stack\att\atts_csf.c
 * (path string ROM 0x6dc934). G2 variants of Packetcraft Cordio r20.05c atts_csf.c
 * (third-party/upstream/cordio/ble-host/sources/stack/att/atts_csf.c); native functions
 * 0x52d508..0x52da0c.
 *
 * Differences from upstream:
 *   - each exported getter/writer rejects connId 0 with a product WARN trace
 *     ("Invalid connId in <func>: %d") and a fixed return (0x0e, nothing, 3);
 *   - ATT_TRACE_xxx uses the G2 ERR/WARN/INFO -> audio_log_extended / WsfTrace cascade;
 *   - the exported getter keeps the TSV spelling AttsCsfGetChangeAwareState
 *     (upstream AttsCsfGetClientChangeAwareState; the stock function-name string is the
 *     upstream one, ROM 0x7524d8).
 * attsCsfIsClientChangeAware 0x52c928 is implemented in ble/ble-att. */
#include <stddef.h>
#include <stdint.h>

/* attsCsfCb (RAM 0x20073e04): +0 attsCsfRec_t table[3] {csf, changeAwareState};
 * +0x08 attsCsfWriteCback_t writeCback. */
extern uint8_t audio_ble_connection_state_table[];

typedef void (*atts_csf_write_cback_t)(uint8_t connId, uint8_t changeAwareState,
                                       uint8_t *pCsf);

extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void WsfTrace(const char *label, const char *format, ...);
extern void audio_uart_checksum_copy(void *destination, const void *source,
                                     uint32_t length); /* 0x439be4 memcpy */

static const char err_label[] = "ERR";   /* inline pool 0x52d7b8 / 0x52da0c */
static const char warn_label[] = "WARN"; /* ROM 0x78cca4 */
static const char info_label[] = "INFO"; /* ROM 0x78cc9c */
static const char att_label[] = "ATT";   /* inline pool 0x52d7bc / 0x52da10 */
static const char hci_label[] = "HCI";   /* inline pool 0x52d7c0 / 0x52da14 */
static const char atts_csf_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\atts_csf.c"; /* ROM 0x6dc934 */
static const char write_name[] = "AttsCsfWriteFeatures";                      /* ROM 0x7756a4 */
static const char write_invalid[] = "Invalid connId in AttsCsfWriteFeatures: %d"; /* ROM 0x73c610 */
static const char write_updated[] = "connId %d updated csf to 0x%02x";       /* ROM 0x75e2d0 */
static const char get_name[] = "AttsCsfGetFeatures";                         /* ROM 0x77e2a8 */
static const char get_invalid[] = "Invalid connId in AttsCsfGetFeatures: %d";  /* ROM 0x73c63c */
static const char state_name[] = "AttsCsfGetClientChangeAwareState";         /* ROM 0x7524d8 */
static const char state_invalid[] =
    "Invalid connId in AttsCsfGetClientChangeAwareState: %d";                /* ROM 0x71c3b8 */

/* Product ATT_TRACE_xxx expansion; every call and compare is emitted in this order. */
#define G2_ATT_TRACE(stat, func, line, ...)                                              \
    do {                                                                                 \
        if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&                           \
            audio_ble_hci_vendor_compare_44b610((stat), err_label, 3u) == 0) {           \
            if ((audio_log_flags() & 2u) != 0u)                                          \
                audio_log_extended(1u, att_label, atts_csf_path, (func), (line), __VA_ARGS__); \
        } else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&                    \
                   audio_ble_hci_vendor_compare_44b610((stat), warn_label, 4u) == 0) {   \
            if ((audio_log_flags() & 2u) != 0u)                                          \
                audio_log_extended(2u, att_label, atts_csf_path, (func), (line), __VA_ARGS__); \
        } else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&                    \
                   audio_ble_hci_vendor_compare_44b610((stat), info_label, 4u) == 0) {   \
            if ((audio_log_flags() & 2u) != 0u)                                          \
                audio_log_extended(3u, att_label, atts_csf_path, (func), (line), __VA_ARGS__); \
        } else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u) {                    \
            if ((audio_log_flags() & 2u) != 0u)                                          \
                audio_log_extended(4u, att_label, atts_csf_path, (func), (line), __VA_ARGS__); \
        } else if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||                    \
                   audio_ble_hci_vendor_compare_44b610(att_label, hci_label, 3u) != 0) { \
            WsfTrace((stat), __VA_ARGS__);                                               \
        }                                                                                \
    } while (0)

#define CSF_REC(connId) (audio_ble_connection_state_table + ((uint32_t)(connId) - 1u) * 2u)

/* Stock 0x52D508 (AttsCsfWriteFeatures) */
uint8_t AttsCsfWriteFeatures_52d508(uint8_t connId, uint16_t offset, uint16_t valueLen,
                                    uint8_t *pValue)
{
    (void)offset;
    if (connId == 0u) {
        G2_ATT_TRACE(warn_label, write_name, 0x172u, write_invalid, connId);
        return 0x0eu; /* ATT_ERR_UNLIKELY */
    }

    uint8_t *pCsfRec = CSF_REC(connId);
    if (valueLen > 1u)
        return 0x0du; /* ATT_ERR_LENGTH */

    uint8_t newCsf = (uint8_t)(*pValue & 7u);
    if (pCsfRec[0] != 0u && newCsf == 0u)
        return 0x13u; /* ATT_ERR_VALUE_NOT_ALLOWED */

    pCsfRec[0] = (uint8_t)(pCsfRec[0] | newCsf);
    G2_ATT_TRACE(info_label, write_name, 0x18cu, write_updated, connId, pCsfRec[0]);

    atts_csf_write_cback_t cback =
        *(atts_csf_write_cback_t *)(void *)(audio_ble_connection_state_table + 8u);
    if (cback != NULL)
        cback(connId, pCsfRec[1], &pCsfRec[0]);
    return 0u;
}

/* Stock 0x52D7C4 (AttsCsfGetFeatures) */
void AttsCsfGetFeatures_52d7c4(uint8_t connId, uint8_t *pCsfOut, uint8_t pCsfOutLen)
{
    if (connId == 0u) {
        G2_ATT_TRACE(warn_label, get_name, 0x1a6u, get_invalid, connId);
        return;
    }
    if (pCsfOutLen <= 1u)
        audio_uart_checksum_copy(pCsfOut, CSF_REC(connId), pCsfOutLen);
}

/* Stock 0x52D8EE (AttsCsfGetChangeAwareState) */
uint8_t AttsCsfGetChangeAwareState_52d8ee(uint8_t connId)
{
    if (connId == 0u) {
        G2_ATT_TRACE(warn_label, state_name, 0x1bcu, state_invalid, connId);
        return 3u;
    }
    return CSF_REC(connId)[1];
}
