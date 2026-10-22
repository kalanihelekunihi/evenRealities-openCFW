/* Stock source: D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-profiles\sources\apps\app\common\app_db.c
 * (path string ROM 0x6d84bc). G2 variant of the AmbiqSuite Cordio app-framework
 * record database; native range 0x47b3e2..0x47b40c.
 *
 * Upstream reference: third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/
 * cordio/ble-profiles/sources/apps/app/common/app_db.c, AppDbSetCccTblValue.
 * Differences in stock:
 *   - WSF_ASSERT(idx < APP_DB_NUM_CCCD) is compiled out;
 *   - the AM_BLE_USE_NVM tail calls the two G2 bond-record persistence routines
 *     (0x479b74, 0x47b730) instead of AppDbUpdateNVM(hdl).
 * The G2 database holds 10 records of 200 bytes (base RAM 0x20067a30);
 * appDbRec_t.cccTbl starts at +0x6c (10 x uint16_t, APP_DB_NUM_CCCD = 10). */
#include <stdint.h>

#define APP_DB_REC_CCC_TBL_OFFSET 0x6cu

extern uint8_t app_conn_is_open_4bb05a(void);                     /* AppConnIsOpen 0x4bb05a */
extern uint8_t audio_ble_connection_is_active_4bad26(uint8_t conn); /* AppCheckBonded 0x4bad26 */
extern uint32_t audio_ble_privacy_rewrite_record(uint8_t *record);  /* 0x479b74 */
extern uint8_t audio_ble_pair_record_validate(uint8_t *record);     /* 0x47b730 */

void AppDbSetCccTblValue_47b3e2(uint8_t *hdl, uint16_t idx, uint16_t value)
{
    uint16_t *ccc_tbl = (uint16_t *)(void *)(hdl + APP_DB_REC_CCC_TBL_OFFSET);
    uint8_t conn_id;

    ccc_tbl[idx] = value;

    conn_id = app_conn_is_open_4bb05a();
    if (audio_ble_connection_is_active_4bad26(conn_id) != 0u) {
        (void)audio_ble_privacy_rewrite_record(hdl);
        (void)audio_ble_pair_record_validate(hdl);
    }
}
